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


# Get the file box of one user.
# Each user has a simple list of saved files.
def get_file_box(data, user_id):
    if "files" not in data:
        data["files"] = {}

    if user_id not in data["files"]:
        data["files"][user_id] = []

    return data["files"][user_id]


# Save the same file into each selected receiver's file box.
def save_file(data, sender, recipient_list, file_name, file_content):
    for recipient in recipient_list:
        file_box = get_file_box(data, recipient)
        new_file = {
            "type": "file",
            "sender": sender,
            "recipients": recipient_list[:],
            "file_name": file_name,
            "content": file_content
        }
        file_box.append(new_file)


# Build one simple inbox title for one item.
def build_inbox_item_title(item):
    if item["type"] == "message":
        return "Message [" + item["sender"] + "]"
    elif item["type"] == "broadcast":
        return "Broadcast [" + item["sender"] + "]"
    elif item["type"] == "file":
        return item["file_name"] + " [" + item["sender"] + "]"
    elif item["type"] == "acknowledgement":
        if item.get("related_type") == "file" and item.get("file_name", "") != "":
            return item["file_name"] + " acknowledgement [" + item["sender"] + "]"
        elif item.get("related_type") == "message":
            return "Message acknowledgement [" + item["sender"] + "]"
        else:
            return "Acknowledgement [" + item["sender"] + "]"
    else:
        return "Item [" + item["sender"] + "]"


# Get all inbox items of one user in one simple list.
# Messages are listed first, then files.
def get_inbox_entries(data, user_id):
    inbox_entries = []
    message_box = get_message_box(data, user_id)
    file_box = get_file_box(data, user_id)

    for i in range(len(message_box)):
        inbox_entries.append({
            "box_name": "messages",
            "box_index": i,
            "item": message_box[i]
        })

    for i in range(len(file_box)):
        inbox_entries.append({
            "box_name": "files",
            "box_index": i,
            "item": file_box[i]
        })

    return inbox_entries


# Get simple inbox titles for display on the client side.
def get_inbox_summary_list(data, user_id):
    inbox_entries = get_inbox_entries(data, user_id)
    summary_list = []

    for entry in inbox_entries:
        summary_list.append(build_inbox_item_title(entry["item"]))

    return summary_list


# Get one inbox entry by a simple 0-based index.
def get_inbox_entry(data, user_id, item_index):
    inbox_entries = get_inbox_entries(data, user_id)

    if item_index < 0 or item_index >= len(inbox_entries):
        return None

    return inbox_entries[item_index]


# Delete one inbox item by a simple 0-based index.
def delete_inbox_item(data, user_id, item_index):
    entry = get_inbox_entry(data, user_id, item_index)

    if entry is None:
        return False

    if entry["box_name"] == "messages":
        message_box = get_message_box(data, user_id)
        message_box.pop(entry["box_index"])
    elif entry["box_name"] == "files":
        file_box = get_file_box(data, user_id)
        file_box.pop(entry["box_index"])
    else:
        return False

    return True


# Save one acknowledgement into the original sender's message box.
def save_acknowledgement(data, receiver, original_sender, related_type, file_name=""):
    message_box = get_message_box(data, original_sender)
    acknowledgement_content = ""

    if related_type == "file":
        acknowledgement_content = "File has been read."
    else:
        acknowledgement_content = "Message has been read."

    new_message = {
        "type": "acknowledgement",
        "sender": receiver,
        "related_type": related_type,
        "content": acknowledgement_content
    }

    if file_name != "":
        new_message["file_name"] = file_name

    message_box.append(new_message)


# Send one acknowledgement after the user reads a normal message or file.
# Acknowledgement items will not create another acknowledgement.
def send_read_acknowledgement(data, reader, entry):
    item = entry["item"]

    if item["type"] == "acknowledgement":
        return False
    if item["type"] == "broadcast":
        return False
    if item.get("ack_sent") == True:
        return False

    if item["type"] == "message":
        save_acknowledgement(data, reader, item["sender"], "message")
        item["ack_sent"] = True
        return True
    elif item["type"] == "file":
        save_acknowledgement(
            data,
            reader,
            item["sender"],
            "file",
            item.get("file_name", "")
        )
        item["ack_sent"] = True
        return True

    return False
