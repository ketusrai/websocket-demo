from flask import Flask, request, jsonify

app = Flask(__name__)


def cast_value(value, target_type):
    """
    简单的类型转换示例，仅演示字符串 -> int/float/bool/str。
    可根据需求扩展更多类型处理。
    """
    try:
        if target_type == "int":
            return int(value)
        elif target_type == "float":
            return float(value)
        elif target_type == "bool":
            # 这里做一个简单判断，非空字符串且非 "0"/"false" 就当作 True
            # 可按需自行改造
            return str(value).lower() not in ["", "0", "false", "none"]
        elif target_type == "str":
            return str(value)
        else:
            # 如果不认识的类型，就原样返回
            return value
    except Exception:
        # 如果转换失败，也原样返回
        return value


@app.route("/execute", methods=["POST"])
def execute_code():
    """
    接口说明：
    1. code: 必填，包含 Python 代码的字符串，其中必须有一个 main(input_data) 函数，并且需要 return。
    2. input: 可选，用于作为 main 函数的参数，建议是一个字典结构。
    3. output: 必填，List[{key: str, type: str}]，表示需要从 main 返回值中获取的字段名和所需转换的类型。
    """
    try:
        req_data = request.get_json(force=True)

        # 获取请求中的参数
        code_str = req_data.get("code", "")
        input_data = req_data.get("input", {})
        output_list = req_data.get("output", [])

        if not code_str:
            return jsonify({"error": "code 字段不能为空"}), 400

        # 准备执行环境
        exec_env = {}

        # 动态执行传入的代码。此操作有安全风险，仅在可信环境使用。
        exec(code_str, exec_env)

        # 检查 main 是否存在
        if "main" not in exec_env or not callable(exec_env["main"]):
            return jsonify({"error": "在传入的 code 中未找到 main 函数或 main 非可调用"}), 400

        # 执行 main 函数，并获取返回值
        main_func = exec_env["main"]
        result = main_func(input_data)

        # 如果返回的不是字典，这里仅做演示处理，直接返回原结果
        if not isinstance(result, dict):
            return jsonify({"result": result}), 200

        # 根据 output 列表指定的 key/type 来获取、转换返回值
        final_output = {}
        for item in output_list:
            key = item.get("key")
            target_type = item.get("type", "str")
            if key in result:
                final_output[key] = cast_value(result[key], target_type)
            else:
                final_output[key] = None  # 若没有此字段，返回 None 或自行处理

        return jsonify(final_output), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)