"""
This file is the server side of the message system.
It receives requests from clients, checks them,
updates the JSON data, and sends replies back.
"""

import socket
import threading

import config
import protocol
import storage

users = {}
server_data = {}

# Read one full request line from the client.
def receive_request(client_socket):
    message = ""

    while "\n" not in message:
        data = client_socket.recv(config.BUFFER_SIZE)
        if not data:
            break

        message = message + data.decode()

    return message.strip()


# Check whether all message receivers are valid.
# The sender can only send messages to people in the friend list.
def check_message_receivers(sender, recipient_list):
    checked_list = []

    for recipient in recipient_list:
        recipient = recipient.strip().lower()

        if recipient == "":
            continue
        if recipient == sender:
            return [], "You cannot send a message to yourself"
        if recipient in checked_list:
            continue
        if not storage.is_friend(server_data, sender, recipient):
            return [], "You can only send messages to your friends"

        checked_list.append(recipient)

    if len(checked_list) == 0:
        return [], "No valid recipient selected"

    return checked_list, ""


# Check whether all file receivers are valid.
# The sender can only send files to people in the friend list.
def check_file_receivers(sender, recipient_list):
    checked_list = []

    for recipient in recipient_list:
        recipient = recipient.strip().lower()

        if recipient == "":
            continue
        if recipient == sender:
            return [], "You cannot send a file to yourself"
        if recipient in checked_list:
            continue
        if not storage.is_friend(server_data, sender, recipient):
            return [], "You can only send files to your friends"

        checked_list.append(recipient)

    if len(checked_list) == 0:
        return [], "No valid recipient selected"

    return checked_list, ""


# Check whether the sender has friends for broadcast.
def get_broadcast_receivers(sender):
    friend_list = storage.get_friend_list(server_data, sender)

    if len(friend_list) == 0:
        return [], "You do not have any friends to broadcast to"

    return friend_list[:], ""


# Check whether the file name is a text file name.
def is_text_file_name(file_name):
    return file_name.lower().endswith(".txt")


# Handle one connected client.
def handle_client(client_socket, client_address):
    print("Client connected:", client_address)
    current_user = ""

    try:
        # Send a simple welcome message after connection.
        client_socket.sendall("Connected to Message System server.\n".encode())

        # Keep reading requests until the client disconnects.
        while True:
            message = receive_request(client_socket)
            if message == "":
                break

            print("Received from", client_address, ":", message)

            parts = protocol.parse_message(message)
            command = parts[0]

            # LOGIN protocol:
            # LOGIN|user_id|password
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

            # VIEW_FRIENDS protocol:
            # VIEW_FRIENDS|user_id
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

            # ADD_FRIEND protocol:
            # ADD_FRIEND|user_id|friend_id
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

            # DELETE_FRIEND protocol:
            # DELETE_FRIEND|user_id|friend_id
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

            # SEND_MESSAGE protocol:
            # SEND_MESSAGE|sender|friend1,friend2|message_content
            # The message content may contain escaped special characters.
            elif command == "SEND_MESSAGE":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "SEND_MESSAGE", "Please login first"
                    )
                else:
                    request_data = protocol.parse_send_message_request(message)

                    if request_data is None:
                        reply = protocol.build_error_response(
                            "SEND_MESSAGE", "Wrong send message format"
                        )
                    else:
                        sender = request_data[0]
                        recipient_list = request_data[1]
                        message_content = request_data[2]

                        if sender != current_user:
                            reply = protocol.build_error_response(
                                "SEND_MESSAGE", "Wrong user"
                            )
                        else:
                            checked_list, error_message = check_message_receivers(
                                sender, recipient_list
                            )

                            if error_message != "":
                                reply = protocol.build_error_response(
                                    "SEND_MESSAGE", error_message
                                )
                            elif message_content.strip() == "":
                                reply = protocol.build_error_response(
                                    "SEND_MESSAGE", "Message cannot be empty"
                                )
                            else:
                                storage.save_message(
                                    server_data, sender, checked_list, message_content
                                )
                                storage.save_server_data(server_data)
                                reply = protocol.build_success_response(
                                    "SEND_MESSAGE", "Message sent successfully"
                                )

            # BROADCAST protocol:
            # BROADCAST|sender|message_content
            elif command == "BROADCAST":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "BROADCAST", "Please login first"
                    )
                else:
                    request_data = protocol.parse_broadcast_request(message)

                    if request_data is None:
                        reply = protocol.build_error_response(
                            "BROADCAST", "Wrong broadcast format"
                        )
                    else:
                        sender = request_data[0]
                        message_content = request_data[1]

                        if sender != current_user:
                            reply = protocol.build_error_response(
                                "BROADCAST", "Wrong user"
                            )
                        else:
                            friend_list, error_message = get_broadcast_receivers(
                                sender
                            )

                            if error_message != "":
                                reply = protocol.build_error_response(
                                    "BROADCAST", error_message
                                )
                            elif message_content.strip() == "":
                                reply = protocol.build_error_response(
                                    "BROADCAST", "Message cannot be empty"
                                )
                            else:
                                storage.save_broadcast_message(
                                    server_data, sender, message_content
                                )
                                storage.save_server_data(server_data)
                                reply = protocol.build_success_response(
                                    "BROADCAST", "Broadcast sent successfully"
                                )

            # SEND_FILE protocol:
            # SEND_FILE|sender|friend1,friend2|file_name|file_content
            elif command == "SEND_FILE":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "SEND_FILE", "Please login first"
                    )
                else:
                    request_data = protocol.parse_send_file_request(message)

                    if request_data is None:
                        reply = protocol.build_error_response(
                            "SEND_FILE", "Wrong send file format"
                        )
                    else:
                        sender = request_data[0]
                        recipient_list = request_data[1]
                        file_name = request_data[2]
                        file_content = request_data[3]

                        if sender != current_user:
                            reply = protocol.build_error_response(
                                "SEND_FILE", "Wrong user"
                            )
                        else:
                            checked_list, error_message = check_file_receivers(
                                sender, recipient_list
                            )

                            if error_message != "":
                                reply = protocol.build_error_response(
                                    "SEND_FILE", error_message
                                )
                            elif not is_text_file_name(file_name):
                                reply = protocol.build_error_response(
                                    "SEND_FILE", "Only text files are allowed"
                                )
                            elif file_content.strip() == "":
                                reply = protocol.build_error_response(
                                    "SEND_FILE", "File content cannot be empty"
                                )
                            else:
                                storage.save_file(
                                    server_data,
                                    sender,
                                    checked_list,
                                    file_name,
                                    file_content
                                )
                                storage.save_server_data(server_data)
                                reply = protocol.build_success_response(
                                    "SEND_FILE", "File sent successfully"
                                )

            # LOGOUT protocol:
            # LOGOUT
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

            # Any unknown command will return an error reply.
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

    # Load user accounts and saved server data before starting the socket.
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
