# This file contains the simple text-based protocol used
# between the client and the server.
# Most requests and replies use "|" as the separator.

"""---- Login Protocol ----"""
# LOGIN request:
# LOGIN|user_id|password
def build_login_request(user_id, password):
    return "LOGIN|" + user_id + "|" + password


# REGISTER request:
# REGISTER|user_id|password
def build_register_request(user_id, password):
    return "REGISTER|" + user_id + "|" + password


"""---- Friend List Management Protocol ----"""
# VIEW_FRIENDS request:
# VIEW_FRIENDS|user_id
def build_view_friends_request(user_id):
    return "VIEW_FRIENDS|" + user_id


# VIEW_FRIENDS_STATUS request:
# VIEW_FRIENDS_STATUS|user_id
def build_view_friends_status_request(user_id):
    return "VIEW_FRIENDS_STATUS|" + user_id


# VIEW_FRIENDS_STATUS success reply:
# OK|VIEW_FRIENDS_STATUS|friend1:online,friend2:offline
def build_view_friends_status_response(friend_status_list):
    entry_list = []

    for friend_status in friend_status_list:
        entry_list.append(friend_status["friend_id"] + ":" + friend_status["status"])

    return "OK|VIEW_FRIENDS_STATUS|" + ",".join(entry_list)


# Parse the VIEW_FRIENDS_STATUS success reply.
def parse_view_friends_status_response(message):
    parts = message.strip().split("|", 2)

    if len(parts) != 3 or parts[0] != "OK" or parts[1] != "VIEW_FRIENDS_STATUS":
        return None

    if parts[2] == "NO_FRIENDS":
        return []

    friend_status_list = []
    entry_list = parts[2].split(",")

    for entry in entry_list:
        friend_and_status = entry.split(":", 1)

        if len(friend_and_status) != 2:
            return None

        friend_status_list.append({
            "friend_id": friend_and_status[0],
            "status": friend_and_status[1]
        })

    return friend_status_list


# ADD_FRIEND request:
# ADD_FRIEND|user_id|friend_id
def build_add_friend_request(user_id, friend_id):
    return "ADD_FRIEND|" + user_id + "|" + friend_id


# DELETE_FRIEND request:
# DELETE_FRIEND|user_id|friend_id
def build_delete_friend_request(user_id, friend_id):
    return "DELETE_FRIEND|" + user_id + "|" + friend_id


"""---- Message Sending Protocol ----"""
# Replace special characters before sending a message.
# This helps multi-line messages work in one text request.
def change_special_text(text):
    text = text.replace("\\", "\\\\")
    text = text.replace("|", "\\p")
    text = text.replace("\n", "\\n")
    return text


# Change the saved special marks back to the original text.
def restore_special_text(text):
    result = ""
    i = 0

    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text):
            next_char = text[i + 1]

            if next_char == "n":
                result = result + "\n"
            elif next_char == "p":
                result = result + "|"
            elif next_char == "\\":
                result = result + "\\"
            else:
                result = result + next_char

            i = i + 2
        else:
            result = result + text[i]
            i = i + 1

    return result


# SEND_MESSAGE request:
# SEND_MESSAGE|sender|friend1,friend2|message_content
def build_send_message_request(user_id, recipient_list, message_content):
    recipients_text = ",".join(recipient_list)
    safe_message_content = change_special_text(message_content)
    return "SEND_MESSAGE|" + user_id + "|" + recipients_text + "|" + safe_message_content


# Parse the SEND_MESSAGE request in a simple way.
# split("|", 3) keeps the message body as one whole part.
def parse_send_message_request(message):
    parts = message.strip().split("|", 3)

    if len(parts) != 4 or parts[0] != "SEND_MESSAGE":
        return None

    user_id = parts[1]

    if parts[2] == "":
        recipient_list = []
    else:
        recipient_list = parts[2].split(",")

    message_content = restore_special_text(parts[3])
    return user_id, recipient_list, message_content


"""---- Broadcast Message Protocol ----"""
# BROADCAST request:
# BROADCAST|sender|message_content
def build_broadcast_request(user_id, message_content):
    safe_message_content = change_special_text(message_content)
    return "BROADCAST|" + user_id + "|" + safe_message_content


# Parse the BROADCAST request in a simple way.
# split("|", 2) keeps the message body as one whole part.
def parse_broadcast_request(message):
    parts = message.strip().split("|", 2)

    if len(parts) != 3 or parts[0] != "BROADCAST":
        return None

    user_id = parts[1]
    message_content = restore_special_text(parts[2])
    return user_id, message_content


"""---- File Sending Protocol ----"""
# SEND_FILE request:
# SEND_FILE|sender|friend1,friend2|file_name|file_content
def build_send_file_request(user_id, recipient_list, file_name, file_content):
    recipients_text = ",".join(recipient_list)
    safe_file_name = change_special_text(file_name)
    safe_file_content = change_special_text(file_content)
    return (
        "SEND_FILE|"
        + user_id
        + "|"
        + recipients_text
        + "|"
        + safe_file_name
        + "|"
        + safe_file_content
    )


# Parse the SEND_FILE request in a simple way.
# split("|", 4) keeps the file content as one whole part.
def parse_send_file_request(message):
    parts = message.strip().split("|", 4)

    if len(parts) != 5 or parts[0] != "SEND_FILE":
        return None

    user_id = parts[1]

    if parts[2] == "":
        recipient_list = []
    else:
        recipient_list = parts[2].split(",")

    file_name = restore_special_text(parts[3])
    file_content = restore_special_text(parts[4])
    return user_id, recipient_list, file_name, file_content


"""---- Inbox Protocol ----"""
# LIST_INBOX request:
# LIST_INBOX|user_id
def build_list_inbox_request(user_id):
    return "LIST_INBOX|" + user_id


# READ_ITEM request:
# READ_ITEM|user_id|item_number
def build_read_item_request(user_id, item_number):
    return "READ_ITEM|" + user_id + "|" + str(item_number)


# DELETE_ITEM request:
# DELETE_ITEM|user_id|item_number
def build_delete_item_request(user_id, item_number):
    return "DELETE_ITEM|" + user_id + "|" + str(item_number)


# LIST_INBOX success reply:
# OK|LIST_INBOX|item_1\nitem_2...
def build_list_inbox_response(summary_list):
    safe_summary_text = change_special_text("\n".join(summary_list))
    return "OK|LIST_INBOX|" + safe_summary_text


# Parse the LIST_INBOX success reply.
def parse_list_inbox_response(message):
    parts = message.strip().split("|", 2)

    if len(parts) != 3 or parts[0] != "OK" or parts[1] != "LIST_INBOX":
        return None

    summary_text = restore_special_text(parts[2])

    if summary_text == "NO_ITEMS":
        return []
    if summary_text == "":
        return []

    return summary_text.split("\n")


# READ_ITEM success reply:
# OK|READ_ITEM|type|sender|detail_1|detail_2|content
def build_read_item_response(item):
    item_type = change_special_text(item["type"])
    sender = change_special_text(item["sender"])
    detail_1 = ""
    detail_2 = ""

    if item["type"] == "file":
        detail_1 = item.get("file_name", "")
    elif item["type"] == "acknowledgement":
        detail_1 = item.get("related_type", "")
        detail_2 = item.get("file_name", "")

    safe_detail_1 = change_special_text(detail_1)
    safe_detail_2 = change_special_text(detail_2)
    safe_content = change_special_text(item.get("content", ""))

    return (
        "OK|READ_ITEM|"
        + item_type
        + "|"
        + sender
        + "|"
        + safe_detail_1
        + "|"
        + safe_detail_2
        + "|"
        + safe_content
    )


# Parse the READ_ITEM success reply.
def parse_read_item_response(message):
    parts = message.strip().split("|", 6)

    if len(parts) != 7 or parts[0] != "OK" or parts[1] != "READ_ITEM":
        return None

    return {
        "type": restore_special_text(parts[2]),
        "sender": restore_special_text(parts[3]),
        "detail_1": restore_special_text(parts[4]),
        "detail_2": restore_special_text(parts[5]),
        "content": restore_special_text(parts[6])
    }


"""---- Server Response Protocol ----"""
# Standard success reply:
# OK|COMMAND|message
def build_success_response(command, message):
    return "OK|" + command + "|" + message


# Standard error reply:
# ERROR|COMMAND|message
def build_error_response(command, message):
    return "ERROR|" + command + "|" + message


# Parse a normal protocol line by "|" for simple commands.
def parse_message(message):
    return message.strip().split("|")
