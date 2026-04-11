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


# Send one request to the server and wait for one reply.
def send_command(client_socket, command):
    client_socket.sendall((command + "\n").encode())
    reply = client_socket.recv(config.BUFFER_SIZE).decode().strip()
    return reply


# Keep asking for login until the server accepts it.
def show_login_screen(client_socket):
    print("==========================")
    print("Welcome to Message System")
    print("==========================")
    print("Please login")

    while True:
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


# Set up the Friend module:view, add, delete
def view_friend_list(client_socket, current_user_id):
    request = protocol.build_view_friends_request(current_user_id)
    reply = send_command(client_socket, request)
    parts = protocol.parse_message(reply)

    if len(parts) >= 3 and parts[0] == "OK" and parts[1] == "VIEW_FRIENDS":
        if parts[2] == "NO_FRIENDS":
            print_box(["Your friend list", "You do not have any friends yet."])
        else:
            friend_list = parts[2].split(",")
            lines = ["Your friend list"]
            for friend_id in friend_list:
                lines.append(friend_id)
            print_box(lines)
    elif len(parts) >= 3:
        print_box(["Error", parts[2]])
    else:
        print_box(["Error", "Invalid response from server"])


def add_new_friend(client_socket, current_user_id):
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
            print("This function is not implemented yet.\n")

        elif choice == "3":
            print("This function is not implemented yet.\n")

        elif choice == "4":
            print("This function is not implemented yet.\n")

        elif choice == "5":
            print("This function is not implemented yet.\n")

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
        client_socket.connect((config.HOST, config.PORT))
        client_socket.recv(config.BUFFER_SIZE).decode().strip()

        while True:
            current_user_id = show_login_screen(client_socket)
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
