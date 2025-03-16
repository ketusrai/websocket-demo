from sqlalchemy import create_engine, event
from sqlalchemy.exc import OperationalError
import time


# 假设你提供一个函数来从外部（如配置文件或其它介质）读取最新的 MySQL 密码
def read_new_password():
    with open('/path/to/mysql_password.txt', 'r') as f:
        return f.read().strip()


# 初始配置：从配置中读取各项参数（可以替换成你自己的逻辑）
SQL_USER = 'root'
current_pwd = '123456'  # 初始密码
SQL_HOST = '127.0.0.1'
SQL_PORT = 3306
SQL_DB = 'agent'


def build_connection_string(pwd):
    return "mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4".format(
        user=SQL_USER,
        pwd=pwd,
        host=SQL_HOST,
        port=SQL_PORT,
        db=SQL_DB
    )


# 创建 engine 时启用 pool_pre_ping 来提前检查连接有效性
engine = create_engine(build_connection_string(current_pwd), pool_pre_ping=True)


# 定义一个刷新 engine 的函数，当检测到认证错误时调用
def refresh_engine():
    global engine, current_pwd
    try:
        new_pwd = read_new_password()
        if new_pwd != current_pwd:
            current_pwd = new_pwd
            # 关闭当前 engine 下的所有连接（使得下次 checkout 创建的连接都会采用新的密码）
            engine.dispose()
            # 重新创建 engine（或更新 engine 的连接字符串，本例中直接创建新 engine）
            engine = create_engine(build_connection_string(new_pwd), pool_pre_ping=True)
            print("Engine refreshed with new password")
    except Exception as e:
        print("Error refreshing engine:", e)


# 通过 event 系统监听 connection checkout 事件
@event.listens_for(engine, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """检查连接状态，如果检测到认证失败，则刷新 engine。
       注意：如果连接已失效，引发异常会使 SQLAlchemy 自动回收该连接。"""
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
    except OperationalError as e:
        # 如果错误提示中含有认证错误，可认为是因为密码变更导致的连接验证失败
        if "Access denied for user" in str(e):
            print("Detected authentication error during checkout; refreshing engine...")
            refresh_engine()
            # 为了确保当前 checkout 失败，新建连接时依然重新检测，所以抛出异常使得 SQLAlchemy 回收该连接
            raise e
        else:
            raise e


# 示例：执行一个简单的查询操作
def test_query():
    with engine.connect() as connection:
        result = connection.execute("SELECT 1").fetchone()
        print("Query result:", result)


if __name__ == '__main__':
    # 首次查询
    test_query()
    # 模拟等待期间密码可能更新，再进行查询
    time.sleep(5)
    test_query()
