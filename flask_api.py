from flask import Flask, request, jsonify
import ast
import tempfile
import subprocess
import os
import json

app = Flask(__name__)

def validate_code_structure(code):
    """静态验证代码结构：检查是否存在main函数和return语句"""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {'valid': False, 'error': f'syntax error: {e}'}

    # 检查是否存在main函数
    main_func = next(
        (n for n in ast.walk(tree)
         if isinstance(n, ast.FunctionDef) and n.name == 'main'), None
    )
    if not main_func:
        return {'valid': False, 'error': 'Undefined main function.'}

    # 检查main函数是否有return语句
    has_return = any(
        isinstance(stmt, ast.Return)
        for stmt in main_func.body
    )
    if not has_return:
        return {'valid': False, 'error': 'Main function missing return statement.'}

    return {'valid': True}


def create_temp_execution_file(code):
    """生成包含安全验证的执行文件"""
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False
    )

    # 添加执行验证代码
    temp_file.write(code)
    temp_file.write('\n\n')
    temp_file.write('''\
import sys
import json

try:
    result = main()
    if not isinstance(result, dict):
        print("ERROR: 返回值必须为字典类型", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(result))
except Exception as e:
    print(f"ERROR: {str(e)}", file=sys.stderr)
    sys.exit(1)
''')
    temp_file.close()
    return temp_file.name


@app.route('/execute', methods=['POST'])
def execute():
    code = request.json.get('code')
    if not code:
        return jsonify({'error': 'Code not provided.'}), 400

    # 静态验证
    static_validation = validate_code_structure(code)
    if not static_validation['valid']:
        return jsonify({'error': static_validation['error']}), 400

    temp_path = None
    try:
        # 创建临时执行文件
        temp_path = create_temp_execution_file(code)

        # 执行代码
        process = subprocess.run(
            ['python', temp_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        # 处理执行结果
        if process.returncode == 2:
            return jsonify({'error': process.stderr.strip()}), 400
        elif process.returncode != 0:
            return jsonify({'error': process.stderr.strip()}), 400

        try:
            result = json.loads(process.stdout)
            if not isinstance(result, dict):
                raise ValueError()
        except:
            return jsonify({'error': 'Return value cannot be parsed as a dictionary.'}), 400

        return jsonify({'result': result})

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Execution timeout.'}), 408
    except Exception as e:
        return jsonify({'error': f'System error.: {str(e)}'}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)