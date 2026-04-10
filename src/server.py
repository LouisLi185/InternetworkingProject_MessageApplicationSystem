import socket
import threading

import config
import protocol
import storage


users = {}


def handle_client(client_socket, client_address):
    print("Client connected:", client_address)
    current_user = ""

    try:
        client_socket.sendall("Connected to Message System server.\n".encode())

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

            elif command == "LOGOUT":
                if current_user == "":
                    reply = "ERROR|LOGOUT|You are not logged in"
                else:
                    reply = "OK|LOGOUT|Goodbye, " + current_user
                    current_user = ""

            else:
                reply = "ERROR|UNKNOWN|This function is not implemented yet"

            client_socket.sendall((reply + "\n").encode())

    except Exception as e:
        print("Error with", client_address, ":", e)

    client_socket.close()
    print("Client disconnected:", client_address)


def main():
    global users

    users = storage.load_default_users()
    storage.load_server_data()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((config.HOST, config.PORT))
    server_socket.listen(5)

    print("Server is listening on", config.HOST, config.PORT)
    print("Default users loaded:", len(users))

    try:
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
