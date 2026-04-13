import os


# Basic server connection settings.
# SERVER_HOST is used by server.py when listening for connections.
# 0.0.0.0 lets the server accept clients from other computers.
SERVER_HOST = "0.0.0.0"

# CLIENT_HOST is used by client.py when connecting to the server.
# For the server computer, 127.0.0.1 is fine.
# For other computers, change this to the server computer IP address.
CLIENT_HOST = "127.0.0.1"

# Use a simple default port for this project.
# If this port is already used on your computer, change it here.
PORT = 12345
BUFFER_SIZE = 1024

# Build file paths from the project base folder.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_USERS_FILE = os.path.join(BASE_DIR, "data", "default_users.json")
SERVER_DATA_FILE = os.path.join(BASE_DIR, "data", "server_data.json")
