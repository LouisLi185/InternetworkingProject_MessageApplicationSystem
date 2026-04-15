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
online_user_counts = {}
online_users_lock = threading.Lock()

# Check the user status.
def mark_user_online(user_id):
    with online_users_lock:
        if user_id not in online_user_counts:
            online_user_counts[user_id] = 0

        online_user_counts[user_id] = online_user_counts[user_id] + 1


def mark_user_offline(user_id):
    with online_users_lock:
        if user_id not in online_user_counts:
            return

        online_user_counts[user_id] = online_user_counts[user_id] - 1

        if online_user_counts[user_id] <= 0:
            del online_user_counts[user_id]


def is_user_online(user_id):
    with online_users_lock:
        return user_id in online_user_counts


def get_friend_status_list(user_id):
    friend_list = storage.get_friend_list(server_data, user_id)
    friend_status_list = []

    for friend_id in friend_list:
        status = "offline"

        if is_user_online(friend_id):
            status = "online"

        friend_status_list.append({
            "friend_id": friend_id,
            "status": status
        })

    return friend_status_list


def change_logged_in_user(current_user, next_user):
    if current_user != "" and current_user != next_user:
        mark_user_offline(current_user)

    if next_user != "" and current_user != next_user:
        mark_user_online(next_user)

    return next_user

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


# Check whether the new user ID format is simple and valid.
def is_valid_new_user_id(user_id):
    if user_id == "":
        return False

    for char in user_id:
        if not (char.islower() or char.isdigit()):
            return False

    return True


# Change the user input number into a simple 0-based inbox index.
def get_inbox_index(number_text):
    try:
        item_number = int(number_text)
    except:
        return None

    if item_number <= 0:
        return None

    return item_number - 1


# Build one simple transfer state after the server accepts TRANSFER_START.
def create_transfer_state(
    sender,
    recipient_list,
    payload_type,
    file_name,
    total_chunks,
    compressed,
    checksum
):
    return {
        "sender": sender,
        "recipient_list": recipient_list,
        "payload_type": payload_type,
        "file_name": file_name,
        "total_chunks": total_chunks,
        "compressed": compressed,
        "checksum": checksum,
        "chunk_list": [""] * total_chunks,
        "received_count": 0
    }


# Save one incoming chunk into the current transfer state.
def save_transfer_chunk(transfer_state, chunk_index, chunk_data):
    list_index = chunk_index - 1

    if list_index < 0 or list_index >= transfer_state["total_chunks"]:
        return False, "Invalid chunk number"

    if transfer_state["chunk_list"][list_index] != "":
        return False, "This chunk was already received"

    transfer_state["chunk_list"][list_index] = chunk_data
    transfer_state["received_count"] = transfer_state["received_count"] + 1
    return True, ""


# Rebuild one finished transfer and continue with the normal save logic.
def finish_transfer(transfer_state):
    encoded_payload = "".join(transfer_state["chunk_list"])
    payload_text, error_message = protocol.restore_transfer_payload(
        encoded_payload,
        transfer_state["compressed"],
        transfer_state["checksum"]
    )

    if error_message != "":
        return False, error_message

    if transfer_state["payload_type"] == "file":
        if not is_text_file_name(transfer_state["file_name"]):
            return False, "Only text files are allowed"
        if payload_text.strip() == "":
            return False, "File content cannot be empty"

        storage.save_file(
            server_data,
            transfer_state["sender"],
            transfer_state["recipient_list"],
            transfer_state["file_name"],
            payload_text
        )
        storage.save_server_data(server_data)
        return True, "File sent successfully"

    return False, "Unsupported transfer type"


# Handle one connected client.
def handle_client(client_socket, client_address):
    print("Client connected:", client_address)
    current_user = ""
    transfer_states = {}

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
                        current_user = change_logged_in_user(current_user, user_id)
                        reply = protocol.build_success_response(
                            "LOGIN", "Welcome, " + user_id
                        )
                    else:
                        reply = protocol.build_error_response(
                            "LOGIN", "Invalid user ID or password"
                        )

            # REGISTER protocol:
            # REGISTER|user_id|password
            elif command == "REGISTER":
                if current_user != "":
                    reply = protocol.build_error_response(
                        "REGISTER", "Please logout first"
                    )
                elif len(parts) != 3:
                    reply = protocol.build_error_response(
                        "REGISTER", "Wrong register format"
                    )
                else:
                    user_id = parts[1].strip().lower()
                    password = parts[2].strip()

                    if not is_valid_new_user_id(user_id):
                        reply = protocol.build_error_response(
                            "REGISTER",
                            "User ID must use lowercase letters or numbers only"
                        )
                    elif password == "":
                        reply = protocol.build_error_response(
                            "REGISTER", "Password cannot be empty"
                        )
                    elif storage.user_exists(users, user_id):
                        reply = protocol.build_error_response(
                            "REGISTER", "User ID already exists"
                        )
                    else:
                        storage.add_user(users, user_id, password)
                        storage.prepare_new_user_data(server_data, user_id)
                        storage.save_default_users(users)
                        storage.save_server_data(server_data)
                        reply = protocol.build_success_response(
                            "REGISTER", "User registered successfully"
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

            # VIEW_FRIENDS_STATUS protocol:
            # VIEW_FRIENDS_STATUS|user_id
            elif command == "VIEW_FRIENDS_STATUS":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "VIEW_FRIENDS_STATUS", "Please login first"
                    )
                elif len(parts) != 2:
                    reply = protocol.build_error_response(
                        "VIEW_FRIENDS_STATUS", "Wrong view friends format"
                    )
                elif parts[1] != current_user:
                    reply = protocol.build_error_response(
                        "VIEW_FRIENDS_STATUS", "Wrong user"
                    )
                else:
                    friend_status_list = get_friend_status_list(current_user)

                    if len(friend_status_list) == 0:
                        reply = protocol.build_success_response(
                            "VIEW_FRIENDS_STATUS", "NO_FRIENDS"
                        )
                    else:
                        reply = protocol.build_view_friends_status_response(
                            friend_status_list
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

            # TRANSFER_START protocol:
            # TRANSFER_START|sender|friend1,friend2|payload_type|transfer_id|file_name|total_chunks|compressed|checksum
            elif command == "TRANSFER_START":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "TRANSFER_START", "Please login first"
                    )
                else:
                    request_data = protocol.parse_transfer_start_request(message)

                    if request_data is None:
                        reply = protocol.build_error_response(
                            "TRANSFER_START", "Wrong transfer start format"
                        )
                    else:
                        sender = request_data[0]
                        recipient_list = request_data[1]
                        payload_type = request_data[2]
                        transfer_id = request_data[3]
                        file_name = request_data[4]
                        total_chunks = request_data[5]
                        compressed = request_data[6]
                        checksum = request_data[7]

                        if sender != current_user:
                            reply = protocol.build_error_response(
                                "TRANSFER_START", "Wrong user"
                            )
                        elif payload_type != "file":
                            reply = protocol.build_error_response(
                                "TRANSFER_START", "Only file transfer is supported"
                            )
                        elif transfer_id.strip() == "":
                            reply = protocol.build_error_response(
                                "TRANSFER_START", "Transfer ID cannot be empty"
                            )
                        elif total_chunks <= 0:
                            reply = protocol.build_error_response(
                                "TRANSFER_START", "Chunk count must be greater than 0"
                            )
                        elif checksum.strip() == "":
                            reply = protocol.build_error_response(
                                "TRANSFER_START", "Checksum cannot be empty"
                            )
                        else:
                            checked_list, error_message = check_file_receivers(
                                sender, recipient_list
                            )

                            if error_message != "":
                                reply = protocol.build_error_response(
                                    "TRANSFER_START", error_message
                                )
                            elif not is_text_file_name(file_name):
                                reply = protocol.build_error_response(
                                    "TRANSFER_START", "Only text files are allowed"
                                )
                            else:
                                transfer_states[transfer_id] = create_transfer_state(
                                    sender,
                                    checked_list,
                                    payload_type,
                                    file_name,
                                    total_chunks,
                                    compressed,
                                    checksum
                                )
                                reply = protocol.build_success_response(
                                    "TRANSFER_START",
                                    "Ready to receive " + str(total_chunks) + " chunk(s)"
                                )

            # TRANSFER_CHUNK protocol:
            # TRANSFER_CHUNK|sender|transfer_id|payload_type|chunk_index|total_chunks|chunk_data
            elif command == "TRANSFER_CHUNK":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "TRANSFER_CHUNK", "Please login first"
                    )
                else:
                    request_data = protocol.parse_transfer_chunk_request(message)

                    if request_data is None:
                        reply = protocol.build_error_response(
                            "TRANSFER_CHUNK", "Wrong transfer chunk format"
                        )
                    else:
                        sender = request_data[0]
                        transfer_id = request_data[1]
                        payload_type = request_data[2]
                        chunk_index = request_data[3]
                        total_chunks = request_data[4]
                        chunk_data = request_data[5]

                        if sender != current_user:
                            reply = protocol.build_error_response(
                                "TRANSFER_CHUNK", "Wrong user"
                            )
                        elif transfer_id not in transfer_states:
                            reply = protocol.build_error_response(
                                "TRANSFER_CHUNK", "Transfer was not started"
                            )
                        else:
                            transfer_state = transfer_states[transfer_id]

                            if payload_type != transfer_state["payload_type"]:
                                reply = protocol.build_error_response(
                                    "TRANSFER_CHUNK", "Transfer type does not match"
                                )
                            elif total_chunks != transfer_state["total_chunks"]:
                                reply = protocol.build_error_response(
                                    "TRANSFER_CHUNK", "Chunk count does not match"
                                )
                            else:
                                save_ok, save_message = save_transfer_chunk(
                                    transfer_state, chunk_index, chunk_data
                                )

                                if not save_ok:
                                    reply = protocol.build_error_response(
                                        "TRANSFER_CHUNK", save_message
                                    )
                                elif transfer_state["received_count"] < transfer_state["total_chunks"]:
                                    reply = protocol.build_success_response(
                                        "TRANSFER_CHUNK",
                                        "Chunk "
                                        + str(chunk_index)
                                        + " of "
                                        + str(total_chunks)
                                        + " received"
                                    )
                                else:
                                    transfer_ok, transfer_message = finish_transfer(
                                        transfer_state
                                    )
                                    del transfer_states[transfer_id]

                                    if transfer_ok:
                                        reply = protocol.build_success_response(
                                            "TRANSFER_CHUNK", transfer_message
                                        )
                                    else:
                                        reply = protocol.build_error_response(
                                            "TRANSFER_CHUNK", transfer_message
                                        )

            # LIST_INBOX protocol:
            # LIST_INBOX|user_id
            elif command == "LIST_INBOX":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "LIST_INBOX", "Please login first"
                    )
                elif len(parts) != 2:
                    reply = protocol.build_error_response(
                        "LIST_INBOX", "Wrong list inbox format"
                    )
                elif parts[1] != current_user:
                    reply = protocol.build_error_response(
                        "LIST_INBOX", "Wrong user"
                    )
                else:
                    summary_list = storage.get_inbox_summary_list(
                        server_data, current_user
                    )

                    if len(summary_list) == 0:
                        reply = protocol.build_success_response(
                            "LIST_INBOX", "NO_ITEMS"
                        )
                    else:
                        reply = protocol.build_list_inbox_response(summary_list)

            # READ_ITEM protocol:
            # READ_ITEM|user_id|item_number
            elif command == "READ_ITEM":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "READ_ITEM", "Please login first"
                    )
                elif len(parts) != 3:
                    reply = protocol.build_error_response(
                        "READ_ITEM", "Wrong read item format"
                    )
                elif parts[1] != current_user:
                    reply = protocol.build_error_response(
                        "READ_ITEM", "Wrong user"
                    )
                else:
                    item_index = get_inbox_index(parts[2])

                    if item_index is None:
                        reply = protocol.build_error_response(
                            "READ_ITEM", "Invalid inbox selection"
                        )
                    else:
                        entry = storage.get_inbox_entry(
                            server_data, current_user, item_index
                        )

                        if entry is None:
                            reply = protocol.build_error_response(
                                "READ_ITEM", "Invalid inbox selection"
                            )
                        else:
                            acknowledgement_sent = storage.send_read_acknowledgement(
                                server_data, current_user, entry
                            )

                            if acknowledgement_sent:
                                storage.save_server_data(server_data)

                            reply = protocol.build_read_item_response(entry["item"])

            # DELETE_ITEM protocol:
            # DELETE_ITEM|user_id|item_number
            elif command == "DELETE_ITEM":
                if current_user == "":
                    reply = protocol.build_error_response(
                        "DELETE_ITEM", "Please login first"
                    )
                elif len(parts) != 3:
                    reply = protocol.build_error_response(
                        "DELETE_ITEM", "Wrong delete item format"
                    )
                elif parts[1] != current_user:
                    reply = protocol.build_error_response(
                        "DELETE_ITEM", "Wrong user"
                    )
                else:
                    item_index = get_inbox_index(parts[2])

                    if item_index is None:
                        reply = protocol.build_error_response(
                            "DELETE_ITEM", "Invalid inbox selection"
                        )
                    else:
                        delete_ok = storage.delete_inbox_item(
                            server_data, current_user, item_index
                        )

                        if not delete_ok:
                            reply = protocol.build_error_response(
                                "DELETE_ITEM", "Invalid inbox selection"
                            )
                        else:
                            storage.save_server_data(server_data)
                            reply = protocol.build_success_response(
                                "DELETE_ITEM", "Item deleted successfully"
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
                    current_user = change_logged_in_user(current_user, "")

            # Any unknown command will return an error reply.
            else:
                reply = protocol.build_error_response(
                    "UNKNOWN", "This function is not implemented yet"
                )

            client_socket.sendall((reply + "\n").encode())

    except Exception as e:
        print("Error with", client_address, ":", e)

    current_user = change_logged_in_user(current_user, "")
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

    try:
        server_socket.bind((config.SERVER_HOST, config.PORT))
    except OSError:
        print("Port", config.PORT, "is already in use.")
        print("Please change PORT in src/config.py and try again.")
        return

    server_socket.listen(5)

    print("Server is listening on", config.SERVER_HOST, config.PORT)
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
