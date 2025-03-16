from functools import wraps
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import config

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)


# 定义数据模型
class User(db.Model):
    __tablename__ = 'users'  # 指定数据表名称为 users
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


# 辅助函数：刷新数据库连接
def refresh_db_connection():
    try:
        # 例如，从指定文件中读取新的密码（实际场景请替换为正确的文件路径和逻辑）
        with open('/path/to/mysql_password.txt', 'r') as f:
            new_pwd = f.read().strip()
        # 更新配置中的密码，并组装新的连接字符串（请确保 config 里有相关的定义）
        app.config['SQL_PWD'] = new_pwd
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            "mysql+pymysql://{SQL_USER}:{SQL_PWD}@{SQL_HOST}:{SQL_PORT}/{SQL_DB}?charset=utf8mb4"
        ).format(
            SQL_USER=app.config.get('SQL_USER', 'root'),
            SQL_PWD=new_pwd,
            SQL_HOST=app.config.get('SQL_HOST', '127.0.0.1'),
            SQL_PORT=app.config.get('SQL_PORT', 3306),
            SQL_DB=app.config.get('SQL_DB', 'agent')
        )
        # 关闭当前连接池，迫使 SQLAlchemy 在下一次请求时重新创建连接
        db.engine.dispose()
        app.logger.info("数据库连接已刷新，使用新密码。")
    except Exception as e:
        app.logger.error("刷新数据库连接时出错：%s", e)


# 装饰器：捕获数据库连接凭证错误，并刷新连接后重试一次数据库操作
def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OperationalError as exc:
            if "Access denied for user" in str(exc):
                app.logger.warning("检测到数据库凭证错误，刷新数据库连接后重试。")
                refresh_db_connection()
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    app.logger.error("刷新后重试数据库操作依然失败：%s", e)
                    return jsonify({'error': '数据库操作失败'}), 500
            else:
                raise  # 其它异常则原样抛出

    return wrapper


# 使用装饰器来包装数据库操作
@handle_db_errors
def add_user():
    # 使用上下文管理器来获得 session，并添加新用户
    with db.session.begin() as session:
        session.add(User(name=config.USER_NAME))
        # 使用 with db.session.begin() 时，退出 with 块时会自动提交事务
    return "User added successfully!"


# Flask 路由中调用 add_user 业务函数
@app.route('/add_user')
def add_user_route():
    try:
        message = add_user()
        return jsonify({"message": message})
    except Exception as e:
        app.logger.error("路由内处理异常：%s", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # 在应用上下文中创建所有数据表
    with app.app_context():
        db.create_all()
    app.run(debug=True)
