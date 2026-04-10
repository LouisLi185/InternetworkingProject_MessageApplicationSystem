import os


HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_USERS_FILE = os.path.join(BASE_DIR, "data", "default_users.json")
SERVER_DATA_FILE = os.path.join(BASE_DIR, "data", "server_data.json")
