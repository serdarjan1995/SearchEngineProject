from os import getenv
from os.path import abspath, dirname

BASE_DIR = dirname(abspath(__file__))

MYSQL_USER = getenv("MYSQL_USER", "mysql")
MYSQL_PASSWORD = getenv("MYSQL_PASSWORD", "mypassword")
MYSQL_DATABASE = getenv("MYSQL_DATABASE", "search_engine")
MYSQL_HOST = getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = getenv("MYSQL_PORT", "3306")

EASY_LIST_PATH = f"{BASE_DIR}/static_data/easylist.txt"
