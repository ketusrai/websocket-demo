import os

SECRET_KEY = os.getenv('SECRET_KEY', 'ai-platform')
CORS_ORIGINS = eval(
    os.getenv('CORS_ORIGINS', "['http://localhost:*']"))
JSON_AS_ASCII = False
REQUEST_TIMEOUT = 120


SQL_USER = os.getenv('SQL_USER', 'root')
SQL_PWD = os.getenv('SQL_PWD', '123456')
SQL_HOST = os.getenv('SQL_HOST', '127.0.0.1')
SQL_PORT = int(os.getenv('SQL_PORT', 3306))
SQL_DB = os.getenv('SQL_DB', 'agent')

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{SQL_USER}:{SQL_PWD}@{SQL_HOST}:{SQL_PORT}/{SQL_DB}?charset=utf8mb4".format(
    SQL_USER=SQL_USER, SQL_PWD=SQL_PWD, SQL_HOST=SQL_HOST, SQL_PORT=SQL_PORT, SQL_DB=SQL_DB)
SQLALCHEMY_POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE', 1000))
SQLALCHEMY_MAX_OVERFLOW = int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', 200))
SQLALCHEMY_ECHO = eval(os.getenv('SQLALCHEMY_ECHO', 'False'))
SQLALCHEMY_RECORD_QUERIES = False
SQLALCHEMY_TRACK_MODIFICATIONS = False


REDIS_IP = os.getenv('REDIS_IP', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_CACHE_DB = int(os.getenv('REDIS_CACHE_DB', 8))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '123456')