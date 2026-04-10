def build_login_request(user_id, password):
    return "LOGIN|" + user_id + "|" + password


def build_success_response(command, message):
    return "OK|" + command + "|" + message


def build_error_response(command, message):
    return "ERROR|" + command + "|" + message


def parse_message(message):
    return message.strip().split("|")
