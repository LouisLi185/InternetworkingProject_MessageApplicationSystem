import json

import config


def load_default_users():
    try:
        file = open(config.DEFAULT_USERS_FILE, "r")
        users = json.load(file)
        file.close()
        return users
    except:
        return {}


def load_server_data():
    try:
        file = open(config.SERVER_DATA_FILE, "r")
        data = json.load(file)
        file.close()
        return data
    except:
        return {}


def save_server_data(data):
    file = open(config.SERVER_DATA_FILE, "w")
    json.dump(data, file, indent=4)
    file.close()


def check_login(users, user_id, password):
    if user_id in users and users[user_id] == password:
        return True
    return False
