import json

import config


# Load the default user accounts from JSON.
def load_default_users():
    try:
        file = open(config.DEFAULT_USERS_FILE, "r")
        users = json.load(file)
        file.close()
        return users
    except:
        return {}


# Load saved server data such as friend lists.
def load_server_data():
    try:
        file = open(config.SERVER_DATA_FILE, "r")
        data = json.load(file)
        file.close()
        return data
    except:
        return {}


# Save the updated server data back to JSON.
def save_server_data(data):
    file = open(config.SERVER_DATA_FILE, "w")
    json.dump(data, file, indent=4)
    file.close()


# Check whether the user ID and password match.
def check_login(users, user_id, password):
    if user_id in users and users[user_id] == password:
        return True
    return False


def prepare_server_data(data, users):
    if "friends" not in data:
        data["friends"] = {}

    if "messages" not in data:
        data["messages"] = {}

    if "files" not in data:
        data["files"] = {}

    for user_id in users:
        if user_id not in data["friends"]:
            data["friends"][user_id] = []

    return data


def user_exists(users, user_id):
    return user_id in users


def get_friend_list(data, user_id):
    if "friends" not in data:
        data["friends"] = {}

    if user_id not in data["friends"]:
        data["friends"][user_id] = []

    return data["friends"][user_id]


def is_friend(data, user_id, friend_id):
    friend_list = get_friend_list(data, user_id)
    return friend_id in friend_list


def add_friend(data, user_id, friend_id):
    friend_list = get_friend_list(data, user_id)
    friend_list.append(friend_id)


def delete_friend(data, user_id, friend_id):
    friend_list = get_friend_list(data, user_id)
    friend_list.remove(friend_id)
