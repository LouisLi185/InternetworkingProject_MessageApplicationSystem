import socket
import threading

import config
import protocol
import storage


users = {}
server_data = {}


# Handle one connected client.
def handle_client(client_socket, client_address):
    print("Client connected:", client_address)
    current_user = ""

    try:
        # Send a simple welcome message after connection.
        client_socket.sendall("Connected to Message System server.\n".encode())

        # Keep reading requests until the client disconnects.
        while True:
            data = client_socket.recv(config.BUFFER_SIZE)
            if not data:
                break

            message = data.decode().strip()
            print("Received from", client_address, ":", message)

            parts = protocol.parse_message(message)
            command = parts[0]

            if command == "LOGIN":
                if len(parts) != 3:
                    reply = protocol.build_error_response("LOGIN", "Wrong login format")
                else:
                    user_id = parts[1]
                    password = parts[2]

                    if storage.check_login(users, user_id, password):
                        current_user = user_id
                        reply = protocol.build_success_response(
                            "LOGIN", "Welcome, " + user_id
                        )
                    else:
                        reply = protocol.build_error_response(
                            "LOGIN", "Invalid user ID or password"
                        )

            elif command == "VIEW_FRIENDS":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "VIEW_FRIENDS", "Please login first"
                    )
                elif len(parts) != 2:
                    reply = protocol.build_error_response(
                        "VIEW_FRIENDS", "Wrong view friends format"
                    )
                elif parts[1] != current_user:
                    reply = protocol.build_error_response(
                        "VIEW_FRIENDS", "Wrong user"
                    )
                else:
                    friend_list = storage.get_friend_list(server_data, current_user)

                    if len(friend_list) == 0:
                        reply = protocol.build_success_response(
                            "VIEW_FRIENDS", "NO_FRIENDS"
                        )
                    else:
                        reply = protocol.build_success_response(
                            "VIEW_FRIENDS", ",".join(friend_list)
                        )

            elif command == "ADD_FRIEND":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "ADD_FRIEND", "Please login first"
                    )
                elif len(parts) != 3:
                    reply = protocol.build_error_response(
                        "ADD_FRIEND", "Wrong add friend format"
                    )
                else:
                    user_id = parts[1]
                    friend_id = parts[2]

                    if user_id != current_user:
                        reply = protocol.build_error_response("ADD_FRIEND", "Wrong user")
                    elif not storage.user_exists(users, friend_id):
                        reply = protocol.build_error_response(
                            "ADD_FRIEND", "User does not exist"
                        )
                    elif friend_id == current_user:
                        reply = protocol.build_error_response(
                            "ADD_FRIEND", "You cannot add yourself"
                        )
                    elif storage.is_friend(server_data, current_user, friend_id):
                        reply = protocol.build_error_response(
                            "ADD_FRIEND", "Already your friend"
                        )
                    else:
                        storage.add_friend(server_data, current_user, friend_id)
                        storage.save_server_data(server_data)
                        reply = protocol.build_success_response(
                            "ADD_FRIEND", "Friend added successfully"
                        )

            elif command == "DELETE_FRIEND":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "DELETE_FRIEND", "Please login first"
                    )
                elif len(parts) != 3:
                    reply = protocol.build_error_response(
                        "DELETE_FRIEND", "Wrong delete friend format"
                    )
                else:
                    user_id = parts[1]
                    friend_id = parts[2]

                    if user_id != current_user:
                        reply = protocol.build_error_response(
                            "DELETE_FRIEND", "Wrong user"
                        )
                    elif not storage.is_friend(server_data, current_user, friend_id):
                        reply = protocol.build_error_response(
                            "DELETE_FRIEND", "This user is not your friend"
                        )
                    else:
                        storage.delete_friend(server_data, current_user, friend_id)
                        storage.save_server_data(server_data)
                        reply = protocol.build_success_response(
                            "DELETE_FRIEND", "Friend deleted successfully"
                        )

            elif command == "LOGOUT":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "LOGOUT", "You are not logged in"
                    )
                else:
                    reply = protocol.build_success_response(
                        "LOGOUT", "Goodbye, " + current_user
                    )
                    current_user = ""

            else:
                reply = protocol.build_error_response(
                    "UNKNOWN", "This function is not implemented yet"
                )

            client_socket.sendall((reply + "\n").encode())

    except Exception as e:
        print("Error with", client_address, ":", e)

    client_socket.close()
    print("Client disconnected:", client_address)


# Start the server and wait for client connections.
def main():
    global users
    global server_data

    users = storage.load_default_users()
    server_data = storage.load_server_data()
    server_data = storage.prepare_server_data(server_data, users)
    storage.save_server_data(server_data)

    # Basic socket setup.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((config.HOST, config.PORT))
    server_socket.listen(5)

    print("Server is listening on", config.HOST, config.PORT)
    print("Default users loaded:", len(users))

    try:
        # Accept new clients one by one.
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer stopped.")

    server_socket.close()


if __name__ == "__main__":
    main()
