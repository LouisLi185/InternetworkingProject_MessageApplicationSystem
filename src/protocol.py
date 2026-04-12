# This file contains the simple text-based protocol used
# between the client and the server.
# Most requests and replies use "|" as the separator.

"""---- Login Protocol ----"""
# LOGIN request:
# LOGIN|user_id|password
def build_login_request(user_id, password):
    return "LOGIN|" + user_id + "|" + password


"""---- Friend List Management Protocol ----"""
# VIEW_FRIENDS request:
# VIEW_FRIENDS|user_id
def build_view_friends_request(user_id):
    return "VIEW_FRIENDS|" + user_id


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
