"""
This file is the client side of the message system.
It shows the menus, gets user input, sends requests,
and displays the replies from the server.
"""

import os
import socket

import config
import protocol

# Print important messages inside a simple text box.
def print_box(lines):
    if type(lines) == str:
        lines = [lines]

    width = 0
    for line in lines:
        if len(line) > width:
            width = len(line)

    border = "+=" + ("=" * width) + "=+"
    print()
    print(border)
    for line in lines:
        print("| " + line.ljust(width) + " |")
    print(border)


# Read one full reply line from the server.
def receive_reply(client_socket):
    reply = ""

    while "\n" not in reply:
        data = client_socket.recv(config.BUFFER_SIZE)
        if not data:
            break

        reply = reply + data.decode()

    return reply.strip()


# Send one request to the server and wait for one reply.
def send_command(client_socket, command):
    client_socket.sendall((command + "\n").encode())
    return receive_reply(client_socket)


# Register one new user account from the client side.
def register_new_user(client_socket):
    print_box("Register a new user")
    user_id = input("Enter new user ID: ").strip().lower()
    password = input("Enter new password: ").strip()

    request = protocol.build_register_request(user_id, password)
    reply = send_command(client_socket, request)
    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[1] == "REGISTER":
        print_box(parts[2])
    else:
        print_box(["Error", "Invalid response from server"])


# Keep asking for login until the server accepts it.
def show_login_screen(client_socket):
    while True:
        print("==========================")
        print("Welcome to Message System")
        print("==========================")
        print("1. Login")
        print("2. Register")
        print("3. Exit program")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            user_id = input("Your user ID: ").strip().lower()
            password = input("Your password: ").strip()

            request = protocol.build_login_request(user_id, password)
            reply = send_command(client_socket, request)
            parts = protocol.parse_message(reply)

            if len(parts) >= 3 and parts[0] == "OK" and parts[1] == "LOGIN":
                print_box(["Login successful", parts[2]])
                return user_id
            elif len(parts) >= 3 and parts[0] == "ERROR" and parts[1] == "LOGIN":
                print_box(["Login failed", parts[2]])
            else:
                print_box(["Login failed", "Invalid response from server"])
        elif choice == "2":
            register_new_user(client_socket)
        elif choice == "3":
            return ""
        else:
            print_box(["Error", "Invalid choice. Please try again."])


# Ask the server for the latest friend list of the current user.
# This helper is used by both the friend module and message module.
def get_friend_list_from_server(client_socket, current_user_id):
    request = protocol.build_view_friends_request(current_user_id)
    reply = send_command(client_socket, request)
    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[0] == "OK" and parts[1] == "VIEW_FRIENDS":
        if parts[2] == "NO_FRIENDS":
            return [], ""
        return parts[2].split(","), ""
    elif len(parts) >= 3:
        return None, parts[2]
    else:
        return None, "Invalid response from server"


# Set up the Friend module:view, add, delete
def view_friend_list(client_socket, current_user_id):
    friend_list, error_message = get_friend_list_from_server(
        client_socket, current_user_id
    )

    if friend_list is None:
        print_box(["Error", error_message])
    elif len(friend_list) == 0:
        print_box(["Your friend list", "You do not have any friends yet."])
    else:
        lines = ["Your friend list"]
        for friend_id in friend_list:
            lines.append(friend_id)
        print_box(lines)


def add_new_friend(client_socket, current_user_id):
    # Sends the ADD_FRIEND protocol request.
    print_box("Add a new friend")
    friend_id = input("Enter friend user ID: ").strip()

    request = protocol.build_add_friend_request(current_user_id, friend_id)
    reply = send_command(client_socket, request)
    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[1] == "ADD_FRIEND":
        print_box(parts[2])
    else:
        print_box(["Error", "Invalid response from server"])


def delete_friend(client_socket, current_user_id):
    # Sends the DELETE_FRIEND protocol request.
    print_box("Delete your friend")
    friend_id = input("Enter friend user ID: ").strip()

    request = protocol.build_delete_friend_request(current_user_id, friend_id)
    reply = send_command(client_socket, request)
    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[1] == "DELETE_FRIEND":
        print_box(parts[2])
    else:
        print_box(["Error", "Invalid response from server"])


# Show the friend menu and handle friend requests.
def show_friend_management_menu(client_socket, current_user_id):
    while True:
        print_box(["Manage your friend list", "Current user: " + current_user_id])
        print("1. View your friends")
        print("2. Add a new friend")
        print("3. Delete your friend")
        print("4. Return to main menu")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            view_friend_list(client_socket, current_user_id)
        elif choice == "2":
            add_new_friend(client_socket, current_user_id)
        elif choice == "3":
            delete_friend(client_socket, current_user_id)
        elif choice == "4":
            print()
            return
        else:
            print_box(["Error", "Invalid choice. Please try again."])


# Let the user choose one or more friends as message receivers.
# Only friends of the current user can be selected here.
def choose_message_receivers(client_socket, current_user_id):
    friend_list, error_message = get_friend_list_from_server(
        client_socket, current_user_id
    )

    if friend_list is None:
        print_box(["Error", error_message])
        return []
    if len(friend_list) == 0:
        print_box(["Send message", "You do not have any friends yet."])
        return []

    lines = ["Send message to your friend(s)", "Your friends"]
    for friend_id in friend_list:
        lines.append(friend_id)
    print_box(lines)
    print("Enter friend IDs one by one.")
    print("Type x when you finish.\n")

    selected_receivers = []

    while True:
        friend_id = input("Friend user ID (x to finish): ").strip().lower()

        if friend_id == "x":
            break
        elif friend_id == "":
            print_box(["Error", "Friend user ID cannot be empty."])
        elif friend_id == current_user_id:
            print_box(["Error", "You cannot send a message to yourself."])
        elif friend_id not in friend_list:
            print_box(["Error", "You can only send messages to your friends."])
        elif friend_id in selected_receivers:
            print_box(["Error", "This friend is already selected."])
        else:
            selected_receivers.append(friend_id)
            print_box(["Recipient added", friend_id])

    return selected_receivers


# Let the user type a single-line or multi-line message.
# Two blank lines in a row mean the message input is finished.
def input_message_content():
    print_box(["Type your message", "Press Enter twice to finish"])

    lines = []
    blank_line_count = 0

    while True:
        line = input()
        lines.append(line)

        if line == "":
            blank_line_count = blank_line_count + 1
        else:
            blank_line_count = 0

        if blank_line_count == 2:
            break

    while len(lines) > 0 and lines[-1] == "":
        lines.pop()

    return "\n".join(lines).strip()


# Build and send the SEND_MESSAGE request to the server.
# The server will check the receivers again before saving the message.
def send_message_to_friends(client_socket, current_user_id):
    selected_receivers = choose_message_receivers(client_socket, current_user_id)

    if len(selected_receivers) == 0:
        print_box(["Send message", "No valid recipient selected"])
        return

    message_content = input_message_content()
    request = protocol.build_send_message_request(
        current_user_id, selected_receivers, message_content
    )
    reply = send_command(client_socket, request)
    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[1] == "SEND_MESSAGE":
        print_box(parts[2])
    else:
        print_box(["Error", "Invalid response from server"])


# Let the user choose one or more friends as file receivers.
# Only friends of the current user can be selected here.
def choose_file_receivers(client_socket, current_user_id):
    friend_list, error_message = get_friend_list_from_server(
        client_socket, current_user_id
    )

    if friend_list is None:
        print_box(["Error", error_message])
        return []
    if len(friend_list) == 0:
        print_box(["Send file", "You do not have any friends yet."])
        return []

    lines = ["Send file to your friend(s)", "Your friends"]
    for friend_id in friend_list:
        lines.append(friend_id)
    print_box(lines)
    print("Enter friend IDs one by one.")
    print("Type x when you finish.\n")

    selected_receivers = []

    while True:
        friend_id = input("Friend user ID (x to finish): ").strip().lower()

        if friend_id == "x":
            break
        elif friend_id == "":
            print_box(["Error", "Friend user ID cannot be empty."])
        elif friend_id == current_user_id:
            print_box(["Error", "You cannot send a file to yourself."])
        elif friend_id not in friend_list:
            print_box(["Error", "You can only send files to your friends."])
        elif friend_id in selected_receivers:
            print_box(["Error", "This friend is already selected."])
        else:
            selected_receivers.append(friend_id)
            print_box(["Recipient added", friend_id])

    return selected_receivers


# Ask the user for a text file name, then read the file content.
# The user can enter the file name directly.
def read_text_file_content():
    while True:
        print_box(["Send a text file", "Enter r to return to main menu"])
        file_name = input("Enter text file name: ").strip()

        if file_name.lower() == "r":
            return None, None, "RETURN"
        if file_name == "":
            print_box(["Send file", "File name cannot be empty"])
            continue
        if not file_name.lower().endswith(".txt"):
            print_box(["Send file", "Only text files are allowed"])
            continue

        file_path = os.path.join(config.BASE_DIR, "text_files", file_name)

        if not os.path.isfile(file_path):
            second_file_path = os.path.join(config.BASE_DIR, file_name)

            if os.path.isfile(second_file_path):
                file_path = second_file_path
            else:
                print_box(["Send file", "File does not exist"])
                continue

        try:
            file = open(file_path, "r")
            file_content = file.read()
            file.close()
        except:
            print_box(["Send file", "Cannot read file"])
            continue

        if file_content.strip() == "":
            print_box(["Send file", "File content cannot be empty"])
            continue

        return os.path.basename(file_path), file_content, ""


# Build and send the SEND_FILE request to the server.
# The server will check the receivers again before saving the file.
def send_file_to_friends(client_socket, current_user_id):
    selected_receivers = choose_file_receivers(client_socket, current_user_id)

    if len(selected_receivers) == 0:
        print_box(["Send file", "No valid recipient selected"])
        return

    file_name, file_content, error_message = read_text_file_content()

    if error_message == "RETURN":
        return

    request = protocol.build_send_file_request(
        current_user_id, selected_receivers, file_name, file_content
    )
    reply = send_command(client_socket, request)
    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[1] == "SEND_FILE":
        print_box(parts[2])
    else:
        print_box(["Error", "Invalid response from server"])


# Ask the server for the latest inbox list of the current user.
def get_inbox_list_from_server(client_socket, current_user_id):
    request = protocol.build_list_inbox_request(current_user_id)
    reply = send_command(client_socket, request)
    summary_list = protocol.parse_list_inbox_response(reply)

    if summary_list is not None:
        return summary_list, ""

    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[1] == "LIST_INBOX":
        return None, parts[2]
    else:
        return None, "Invalid response from server"


# Read one inbox item from the server by item number.
def read_inbox_item_from_server(client_socket, current_user_id, item_number):
    request = protocol.build_read_item_request(current_user_id, item_number)
    reply = send_command(client_socket, request)
    item_data = protocol.parse_read_item_response(reply)

    if item_data is not None:
        return item_data, ""

    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[1] == "READ_ITEM":
        return None, parts[2]
    else:
        return None, "Invalid response from server"


# Delete one inbox item on the server by item number.
def delete_inbox_item_from_server(client_socket, current_user_id, item_number):
    request = protocol.build_delete_item_request(current_user_id, item_number)
    reply = send_command(client_socket, request)
    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[1] == "DELETE_ITEM":
        return parts[0] == "OK", parts[2]
    else:
        return False, "Invalid response from server"


# Show one inbox item clearly after the user chooses it.
def show_inbox_item(item_data):
    lines = []

    if item_data["type"] == "message":
        lines.append("Message from " + item_data["sender"])
        lines.append("Content")
    elif item_data["type"] == "broadcast":
        lines.append("Broadcast from " + item_data["sender"])
        lines.append("Content")
    elif item_data["type"] == "file":
        lines.append("File from " + item_data["sender"])
        lines.append("File name: " + item_data["detail_1"])
        lines.append("File content")
    elif item_data["type"] == "acknowledgement":
        lines.append("Acknowledgement from " + item_data["sender"])
        if item_data["detail_1"] == "file" and item_data["detail_2"] != "":
            lines.append("File name: " + item_data["detail_2"])
        lines.append("Content")
    else:
        lines.append("Inbox item from " + item_data["sender"])
        lines.append("Content")

    content_lines = item_data["content"].split("\n")

    for line in content_lines:
        lines.append(line)

    print_box(lines)


# Show the inbox list, read one item, and let the user delete it.
def show_inbox_menu(client_socket, current_user_id):
    while True:
        summary_list, error_message = get_inbox_list_from_server(
            client_socket, current_user_id
        )

        if summary_list is None:
            print_box(["Error", error_message])
            return
        if len(summary_list) == 0:
            print_box(["Your inbox", "Your inbox is empty."])
            return

        lines = ["Your inbox"]

        for i in range(len(summary_list)):
            lines.append(str(i + 1) + ". " + summary_list[i])

        print_box(lines)
        print("Enter r to return to main menu.\n")

        choice = input("Enter item number to read: ").strip().lower()

        if choice == "r":
            print()
            return
        if not choice.isdigit():
            print_box(["Error", "Invalid choice. Please try again."])
            continue

        item_data, error_message = read_inbox_item_from_server(
            client_socket, current_user_id, choice
        )

        if item_data is None:
            print_box(["Error", error_message])
            continue

        show_inbox_item(item_data)

        while True:
            print("1. Delete this item")
            print("2. Return to inbox list")

            action = input("Enter your choice: ").strip()

            if action == "1":
                delete_ok, delete_message = delete_inbox_item_from_server(
                    client_socket, current_user_id, choice
                )

                if delete_ok:
                    print_box(["Delete item", delete_message])
                else:
                    print_box(["Error", delete_message])

                break
            elif action == "2":
                print()
                break
            else:
                print_box(["Error", "Invalid choice. Please try again."])


# Send one message to all friends in the current user's friend list.
# This uses the same multi-line message input as the normal message module.
def broadcast_message_to_all_friends(client_socket, current_user_id):
    friend_list, error_message = get_friend_list_from_server(
        client_socket, current_user_id
    )

    if friend_list is None:
        print_box(["Error", error_message])
        return
    if len(friend_list) == 0:
        print_box(["Broadcast message", "You do not have any friends to broadcast to."])
        return

    lines = ["Broadcast message to all friends", "Your friends"]
    for friend_id in friend_list:
        lines.append(friend_id)
    print_box(lines)

    message_content = input_message_content()
    request = protocol.build_broadcast_request(current_user_id, message_content)
    reply = send_command(client_socket, request)
    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[1] == "BROADCAST":
        print_box(parts[2])
    else:
        print_box(["Error", "Invalid response from server"])


# Show the main menu after login.
def show_main_menu(client_socket, current_user_id):
    while True:
        print_box(["Main Menu", "Current user: " + current_user_id])
        print("1. Manage your friend list")
        print("2. Send message to your friend(s)")
        print("3. Broadcast message to all friends")
        print("4. Send file to your friend(s)")
        print("5. View your messages and files")
        print("6. Logout")
        print("7. Exit program")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_friend_management_menu(client_socket, current_user_id)

        elif choice == "2":
            send_message_to_friends(client_socket, current_user_id)

        elif choice == "3":
            broadcast_message_to_all_friends(client_socket, current_user_id)

        elif choice == "4":
            send_file_to_friends(client_socket, current_user_id)

        elif choice == "5":
            show_inbox_menu(client_socket, current_user_id)

        elif choice == "6":
            reply = send_command(client_socket, "LOGOUT")
            parts = protocol.parse_message(reply)
            if len(parts) >= 3 and parts[0] == "OK" and parts[1] == "LOGOUT":
                print_box(["Logout", parts[2]])
            elif len(parts) >= 3:
                print_box(["Error", parts[2]])
            else:
                print_box(["Error", "Invalid response from server"])
            return True

        elif choice == "7":
            return False

        else:
            print_box(["Error", "Invalid choice. Please try again."])


# Connect to the server and start the client interface.
def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server first, then wait for the welcome line.
        client_socket.connect((config.CLIENT_HOST, config.PORT))
        receive_reply(client_socket)

        while True:
            # After logout, the program will show the login screen again.
            current_user_id = show_login_screen(client_socket)

            if current_user_id == "":
                break

            should_continue = show_main_menu(client_socket, current_user_id)
            if not should_continue:
                break

    except KeyboardInterrupt:
        print_box("Client stopped.")
    except Exception as e:
        print_box(["Connection error", str(e)])

    client_socket.close()


if __name__ == "__main__":
    main()
