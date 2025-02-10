from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)


@app.route("/run", methods=["POST"])
def run_code():
    """
    接口接收 JSON 格式的 POST 请求，请求体样例：

    {
      "code": "def main(a, b):\n    # 示例代码，返回一个字典\n    result = a + b\n    return {'result': result, 'msg': 'success'}\n",
      "input": {"a": 3, "b": 5},
      "output": [
          {"key": "result", "type": "int"},
          {"key": "msg", "type": "str"}
      ]
    }

    其中：
      • code：包含一段 Python 代码，该代码内必须定义 main 函数，并且 main 函数必须有 return 返回值。
      • input：main 函数所需的参数（以 key/value 的形式）。
      • output：对 main 函数返回结果的字段及其对应类型（例如 int、str、float 等），
                接口将尝试将返回结果中对应的字段转换为指定类型，并返回转换后的结果。
    """
    try:
        # 获取 JSON 数据
        data = request.get_json(force=True)
        code = data.get("code", "")
        input_params = data.get("input", {})
        output_spec = data.get("output", [])

        if not code:
            return jsonify({"error": "缺少代码参数 code"}), 400

        # 创建一个空的命名空间来执行用户提供的代码
        local_namespace = {}
        try:
            # 注意：直接使用 exec 执行用户代码存在安全风险
            exec(code, {}, local_namespace)
        except Exception as e:
            return jsonify({"error": "代码执行错误", "detail": traceback.format_exc()}), 400

        # 检查 main 函数是否存在
        if "main" not in local_namespace or not callable(local_namespace["main"]):
            return jsonify({"error": "代码中必须定义 main 函数"}), 400

        main_func = local_namespace["main"]

        # 调用 main 函数，传入 input 参数
        try:
            # 假设 input_params 是传递给 main 的关键字参数
            ret = main_func(**input_params)
        except Exception as e:
            return jsonify({"error": "调用 main 函数发生异常", "detail": traceback.format_exc()}), 400

        # 如果提供了 output 配置，并且返回结果为 dict，则按照 output 参数转换对应的字段类型
        if output_spec and isinstance(ret, dict):
            out_dict = {}
            for spec in output_spec:
                key = spec.get("key")
                t = spec.get("type", "").lower()
                # 如果返回结果中包含该 key，则进行类型转换
                if key in ret:
                    val = ret[key]
                    try:
                        if t == "int":
                            out_dict[key] = int(val)
                        elif t == "float":
                            out_dict[key] = float(val)
                        elif t == "str":
                            out_dict[key] = str(val)
                        elif t == "bool":
                            out_dict[key] = bool(val)
                        elif t == "list":
                            # 如果本身就是 list，则直接返回，否则包装成 list
                            out_dict[key] = val if isinstance(val, list) else [val]
                        else:
                            # 未识别的类型则直接返回原值
                            out_dict[key] = val
                    except Exception as conv_e:
                        # 出现类型转换异常，返回原值或提示错误信息
                        out_dict[key] = val
                else:
                    out_dict[key] = None
            return jsonify({"result": out_dict})
        else:
            # 如果没有 output 选项，或者返回结果不是字典，则直接返回返回值
            return jsonify({"result": ret})

    except Exception as ex:
        return jsonify({"error": "Internal Server Error", "detail": traceback.format_exc()}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)