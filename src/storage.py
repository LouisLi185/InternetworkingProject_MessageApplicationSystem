"""
This file handles reading and writing the JSON data files.
It keeps the storage logic simple for the server.
"""

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


# Prepare missing top-level parts in server_data.json.
# This keeps the data file ready for friend, message, and file modules.
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

        if user_id not in data["messages"]:
            data["messages"][user_id] = []

        if user_id not in data["files"]:
            data["files"][user_id] = []

    return data


# Check whether a user ID exists in the default user list.
def user_exists(users, user_id):
    return user_id in users


# Get the current friend list of one user.
# If the list does not exist yet, create an empty one first.
def get_friend_list(data, user_id):
    if "friends" not in data:
        data["friends"] = {}

    if user_id not in data["friends"]:
        data["friends"][user_id] = []

    return data["friends"][user_id]


# Check whether friend_id is already inside the user's friend list.
def is_friend(data, user_id, friend_id):
    friend_list = get_friend_list(data, user_id)
    return friend_id in friend_list


# Add one friend ID into the user's friend list.
def add_friend(data, user_id, friend_id):
    friend_list = get_friend_list(data, user_id)
    friend_list.append(friend_id)


# Remove one friend ID from the user's friend list.
def delete_friend(data, user_id, friend_id):
    friend_list = get_friend_list(data, user_id)
    friend_list.remove(friend_id)


# Get the message box of one user.
# Each user has a simple list of saved messages.
def get_message_box(data, user_id):
    if "messages" not in data:
        data["messages"] = {}

    if user_id not in data["messages"]:
        data["messages"][user_id] = []

    return data["messages"][user_id]


# Save the same message into each selected receiver's message box.
def save_message(data, sender, recipient_list, message_content):
    for recipient in recipient_list:
        message_box = get_message_box(data, recipient)
        new_message = {
            "type": "message",
            "sender": sender,
            "recipients": recipient_list[:],
            "content": message_content
        }
        message_box.append(new_message)


# Save one broadcast message into every friend's message box.
def save_broadcast_message(data, sender, message_content):
    recipient_list = get_friend_list(data, sender)[:]

    for recipient in recipient_list:
        message_box = get_message_box(data, recipient)
        new_message = {
            "type": "broadcast",
            "sender": sender,
            "recipients": recipient_list[:],
            "content": message_content
        }
        message_box.append(new_message)
