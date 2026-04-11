def build_login_request(user_id, password):
    return "LOGIN|" + user_id + "|" + password


def build_view_friends_request(user_id):
    return "VIEW_FRIENDS|" + user_id


def build_add_friend_request(user_id, friend_id):
    return "ADD_FRIEND|" + user_id + "|" + friend_id


def build_delete_friend_request(user_id, friend_id):
    return "DELETE_FRIEND|" + user_id + "|" + friend_id


def build_success_response(command, message):
    return "OK|" + command + "|" + message


def build_error_response(command, message):
    return "ERROR|" + command + "|" + message


def parse_message(message):
    return message.strip().split("|")
