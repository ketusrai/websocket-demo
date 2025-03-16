import os
from functools import wraps
from flask import Flask, jsonify
import redis
from redis.exceptions import AuthenticationError, RedisError
import config
app = Flask(__name__)
app.config.from_object(config)
# 初始化 Redis 客户端，密码从 app.config 中读取
redis_client = redis.Redis(
    host=app.config.get('REDIS_HOST', '127.0.0.1'),
    port=app.config.get('REDIS_PORT', 6379),
    password=app.config.get('REDIS_PWD', 'default_pwd'),
    decode_responses=True
)
# 辅助函数：从文件中读取最新 Redis 密码，并更新客户端连接
def refresh_redis_connection():
    global redis_client
    try:
        with open('/path/to/redis_password.txt', 'r') as f:
            new_pwd = f.read().strip()
        app.config['REDIS_PWD'] = new_pwd
        redis_client = redis.Redis(
            host=app.config.get('REDIS_HOST', '127.0.0.1'),
            port=app.config.get('REDIS_PORT', 6379),
            password=new_pwd,
            decode_responses=True
        )
        app.logger.info("刷新 Redis 连接成功，新密码已生效。")
    except Exception as e:
        app.logger.error("刷新 Redis 连接时出错: %s", e)
# 装饰器：自动捕获 Redis 的认证错误并刷新连接后重试一次
def handle_redis_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuthenticationError as exc:
            app.logger.warning("检测到 Redis 认证失败 (%s)，正在刷新连接...", exc)
            refresh_redis_connection()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                app.logger.error("刷新 Redis 连接后重试仍失败: %s", e)
                return jsonify({'error': 'Redis 操作失败'}), 500
        except RedisError as exc:
            app.logger.error("Redis 出现错误: %s", exc)
            return jsonify({'error': 'Redis 操作失败'}), 500
    return wrapper
# 示例 1：在路由中使用装饰器直接包装 Redis 操作
@app.route('/redis_get')
@handle_redis_errors
def redis_get():
    # 从 Redis 中获取键 "foo" 的值
    result = redis_client.get('foo')
    return jsonify({'foo': result})
# 示例 2：在业务函数中使用装饰器包装 Redis 操作
@handle_redis_errors
def some_redis_operation():
    # 示例：写入并读取 Redis 中的键值对
    redis_client.set('bar', 'baz')
    return redis_client.get('bar')
@app.route('/redis_op')
def redis_op():
    result = some_redis_operation()
    return jsonify({'bar': result})
if __name__ == '__main__':
    app.run(debug=True)