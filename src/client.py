import getpass
import socket

import config
import protocol


def send_command(client_socket, command):
    client_socket.sendall((command + "\n").encode())
    reply = client_socket.recv(config.BUFFER_SIZE).decode().strip()
    return reply


def show_login_screen(client_socket):
    print("\nWelcome to Message System")
    print("-------------------------")
    print("Please login")

    while True:
        user_id = input("Your user ID: ").strip()
        password = getpass.getpass("Your password: ")

        request = protocol.build_login_request(user_id, password)
        reply = send_command(client_socket, request)
        parts = protocol.parse_message(reply)

        if len(parts) >= 3 and parts[0] == "OK" and parts[1] == "LOGIN":
            print(parts[2])
            return user_id
        elif len(parts) >= 3 and parts[0] == "ERROR" and parts[1] == "LOGIN":
            print("Login failed:", parts[2])
            print()
        else:
            print("Login failed: Invalid response from server")
            print()


def show_friend_management_menu():
    while True:
        print("\nManage your friend list")
        print("-----------------------")
        print("1. View your friends")
        print("2. Add a new friend")
        print("3. Delete your friend")
        print("4. Return to main menu")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            print("This function is not implemented yet.\n")
        elif choice == "2":
            print("This function is not implemented yet.\n")
        elif choice == "3":
            print("This function is not implemented yet.\n")
        elif choice == "4":
            print()
            return
        else:
            print("Invalid choice. Please try again.\n")


def show_main_menu(client_socket, current_user_id):
    while True:
        print("Main Menu")
        print("---------")
        print("Current user:", current_user_id)
        print("1. Manage your friend list")
        print("2. Send message to your friend(s)")
        print("3. Broadcast message to all friends")
        print("4. Send file to your friend(s)")
        print("5. View your messages and files")
        print("6. Logout")
        print("7. Exit program")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_friend_management_menu()

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
                print(parts[2])
            elif len(parts) >= 3:
                print("Error:", parts[2])
            else:
                print("Error: Invalid response from server")
            print()
            return True

        elif choice == "7":
            return False

        else:
            print("Invalid choice. Please try again.\n")


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((config.HOST, config.PORT))
        print("Connected to server at", config.HOST, config.PORT)

        welcome = client_socket.recv(config.BUFFER_SIZE).decode().strip()
        print(welcome)

        while True:
            current_user_id = show_login_screen(client_socket)
            should_continue = show_main_menu(client_socket, current_user_id)
            if not should_continue:
                break

    except KeyboardInterrupt:
        print("\nClient stopped.")
    except Exception as e:
        print("Connection error:", e)

    client_socket.close()


if __name__ == "__main__":
    main()
