import json
import re
from typing import TypedDict, Annotated

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, AIMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.types import Command, interrupt

# 1. define memory
memory = MemorySaver()

# 2. define llm
llm = ChatOpenAI(model="gpt-4o",  temperature=0)

# 3. define state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    order_params: dict
    extract_completed: bool
    confirmed: bool
    order_result: str
    intention: str

def output_paser(json_str: str) -> dict:
    match = re.search(r'\{.*?\}', json_str, re.DOTALL)
    if match:
        json_string = match.group(0)
        # 使用 json.loads() 将字符串解析为 JSON 对象
        return json.loads(json_string)
    else:
        raise ValueError(f'Could not parse JSON string {json_str}')

INTENT_TEMPLATE = '''
# Content
你是一个意图判断专家，请根据历史对话以及最新会话进行意图判断

# Objective
请跟<历史对话>，以及<最新消息>对用户的意图进行分类

<历史对话>
{char_history}

<最新消息>
{latest_message}

# Response
请以json格式进行输出，如下：
{{
    intent: \\ 如果是要求下单，输出"YES"， 否则输出"NO"
}}

'''

# 4. define node and condition
def intent_recognition(state: State):

    chat_history = []
    if state["messages"][:-2]:
        for message in state["messages"][-2]:
            chat_history.append("User : " if isinstance(message, HumanMessage) else "Assistant : " + message.content)

        chat_history = "\n".join(chat_history)

    prompt = INTENT_TEMPLATE.format(char_history=chat_history if chat_history else "" , latest_message=state["messages"][-1].content)
    response = llm.invoke([HumanMessage(content=prompt)])
    response = output_paser(response.content)

    state_update = {
        "intention": response['intent']
    }

    return Command(update=state_update)

def ai_replay_not_in_range(state: State):
    state_update = {
        "messages": [AIMessage(content='我不能处理非下单的问题')]
    }
    return Command(update=state_update)

def extract_params(state: State):
    messages = state["messages"]
    last_message = messages[-1].content

    # 使用LLM提取参数
    prompt = ChatPromptTemplate.from_messages([
        ("system", "提取用户消息中的订单参数：sku号、日期、数量"),
        ("user", "{input}")
    ])
    chain = prompt | llm.with_structured_output(
        schema={
            "title": "OrderParams",  # 添加title
            "description": "订单参数结构",  # 添加description
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "商品SKU编号"  # 添加字段描述
                },
                "date": {
                    "type": "string",
                    "description": "下单日期（YYYY-MM-DD格式）"
                },
                "quantity": {
                    "type": "integer",
                    "description": "订购数量"
                }
            },
            "required": ["sku", "date", "quantity"]
        }
    )
    params = chain.invoke({"input": last_message})

    state_update = {"order_params": params}

    for key, value in state.get('order_params', {}).items():
        if value and not state_update["order_params"][key]:
            state_update["order_params"][key] = value

    return Command(update=state_update)


def extract_conditions(state: State):
    order_params = state["order_params"]
    if not all([order_params['sku'], order_params['date'], order_params['quantity']]):
        return "NO"
    return "YES"

def ai_replay_incomplete_information(state: State):
    order_params = state["order_params"]
    return Command(update={"messages": [AIMessage(content=f'''请提供完整的订单信息
        sku: {order_params['sku']}
        date: {order_params['date']}
        quantity: {order_params['quantity']}''')],
            "extract_completed": False})

def human_interrupt_for_complete_information(query: str):
    human_interrupt = interrupt({'query': query})
    return Command(update={"messages": HumanMessage(content=human_interrupt['data'])})

@tool
def place_order(sku: str, date: str, quantity: int) -> str:
    """实际的下单接口，这里模拟实现"""
    import random
    if random.random() < 0.5:  # 50%成功率
        return "SUCCEEDED"
    return "FAILED"


def ai_replay_confirm(state: State):
    order_params = state["order_params"]
    return Command(update={"messages": [AIMessage(content=f'''请确认是否对此下单:
        sku: {order_params['sku']}
        date: {order_params['date']}
        quantity: {order_params['quantity']}''')],
           "extract_completed": True})


def human_interrupt_for_2nd_confirm(query: str):
    human_interrupt = interrupt({'query': query})
    if human_interrupt['data'].lower() in ["yes", "y", "是的"]:
        state_update = {
            "messages": HumanMessage(content=human_interrupt['data']),
            "confirmed": True
        }
    else:
        state_update = {
            "messages": HumanMessage(content=human_interrupt['data']),
            "confirmed": False
        }
    return Command(update=state_update)


def execute_order(state: State):
    params = state["order_params"]
    result = place_order.invoke(params)
    state_update = {
        "order_result": result
    }
    if result:
        state_update['messages'] = [AIMessage(content=f"订单已成功下单")]
    else:
        state_update['messages'] = [AIMessage(content=f"订单下单失败")]

    return Command(update=state_update)


def ai_replay_cancel(state: State):
    return Command(update={"messages": [AIMessage(content="订单已取消")]})

# 5. 构建工作流程
graph_builder = StateGraph(State)
graph_builder.add_node("intent_recognition", intent_recognition)
graph_builder.add_node("ai_replay_not_in_range", ai_replay_not_in_range)
graph_builder.add_node("extract_params", extract_params)
graph_builder.add_node("ai_replay_incomplete_information", ai_replay_incomplete_information)
graph_builder.add_node("human_interrupt_for_complete_information", human_interrupt_for_complete_information)
graph_builder.add_node("ai_replay_confirm", ai_replay_confirm)
graph_builder.add_node("human_interrupt_for_2nd_confirm", human_interrupt_for_2nd_confirm)
graph_builder.add_node("execute_order", execute_order)
graph_builder.add_node("ai_replay_cancel", ai_replay_cancel)
graph_builder.set_entry_point("intent_recognition")
graph_builder.add_conditional_edges("intent_recognition",
                                    lambda state: state["intention"],
                                    {"YES": "extract_params", "NO": "ai_replay_not_in_range"})
graph_builder.add_edge("ai_replay_not_in_range", END)
graph_builder.add_conditional_edges("extract_params",
                                    extract_conditions,
                                    {"YES": "ai_replay_confirm", "NO": "ai_replay_incomplete_information"})
graph_builder.add_edge("ai_replay_incomplete_information", "human_interrupt_for_complete_information")
graph_builder.add_edge("human_interrupt_for_complete_information", "extract_params")
graph_builder.add_edge("ai_replay_confirm", "human_interrupt_for_2nd_confirm")
graph_builder.add_conditional_edges("human_interrupt_for_2nd_confirm",
                                    lambda state: state["confirmed"],
                                    {True: "execute_order", False: "ai_replay_cancel"})
graph_builder.add_edge("human_interrupt_for_complete_information", "extract_params")
graph_builder.add_edge("execute_order", END)
graph_builder.add_edge("ai_replay_cancel", END)
graph = graph_builder.compile(checkpointer=memory)



from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass



config = {"configurable": {"thread_id": "9"}}

# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream(
    {"messages": [{"role": "user", "content": "我要下单"}]},
    config,
    stream_mode="values")

reply_list = []

for event in events:
    if isinstance(event["messages"][-1], AIMessage):
        reply_list.append(event["messages"][-1].pretty_print)

reply_list[-1]()



human_response = input("YOU:")
human_command = Command(resume={"data": human_response})

events = graph.stream(human_command, config, stream_mode="values")
reply_list = []

for event in events:
    if isinstance(event["messages"][-1], AIMessage):
        reply_list.append(event["messages"][-1].pretty_print)

reply_list[-1]()


human_response = input("YOU:")
human_command = Command(resume={"data": human_response})

events = graph.stream(human_command, config, stream_mode="values")
reply_list = []

for event in events:
    if isinstance(event["messages"][-1], AIMessage):
        reply_list.append(event["messages"][-1].pretty_print)

reply_list[-1]()



state = graph.get_state(config=config)
print(state.next)



!curl https://api.openai.com/v1/chat/completions
