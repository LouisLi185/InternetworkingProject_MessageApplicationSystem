"""
This file is a simple Tkinter GUI client for the message system.
It keeps the current server and protocol, but shows the features
in a clearer and more comfortable desktop window.
"""

import os
import socket
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import client
import config
import protocol


class GuiClientApp:
    def __init__(self, root):
        self.root = root
        self.client_socket = None
        self.current_user_id = ""
        self.friend_status_list = []
        self.inbox_summary_list = []

        self.connection_text = tk.StringVar()
        self.login_result_text = tk.StringVar()
        self.current_user_text = tk.StringVar(value="Current user: -")
        self.user_status_text = tk.StringVar(value="User status: offline")
        self.status_text = tk.StringVar(value="Ready.")
        self.login_result_default_color = "#1f1f1f"
        self.login_result_error_color = "#7a0019"
        self.login_user_var = tk.StringVar()
        self.login_password_var = tk.StringVar()
        self.friend_id_var = tk.StringVar()
        self.message_recipients_var = tk.StringVar()
        self.file_recipients_var = tk.StringVar()
        self.file_path_var = tk.StringVar()

        self.build_window()
        self.show_login_frame()
        self.connect_to_server()

    # Build the main window and all GUI sections.
    def build_window(self):
        self.root.title("Message System GUI Client")
        self.root.geometry("1100x700")
        self.root.minsize(920, 620)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self.close_program)

        self.main_container = ttk.Frame(self.root, padding=12)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)

        self.login_frame = ttk.Frame(self.main_container, padding=18)
        self.main_frame = ttk.Frame(self.main_container, padding=8)

        self.build_login_frame()
        self.build_main_frame()

        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_text,
            anchor="w",
            relief="sunken",
            padding=(8, 4)
        )
        status_bar.grid(row=1, column=0, sticky="ew")

    # Build the first login and register screen.
    def build_login_frame(self):
        self.login_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(
            self.login_frame,
            text="Message System",
            font=("TkDefaultFont", 15, "bold")
        )
        title_label.grid(row=0, column=0, pady=(25, 6))

        info_label = ttk.Label(
            self.login_frame,
            text="Use your user ID and password to login or register."
        )
        info_label.grid(row=1, column=0, pady=(0, 16))

        form_frame = ttk.LabelFrame(
            self.login_frame,
            text="Login / Register",
            padding=16
        )
        form_frame.grid(row=2, column=0)
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="User ID").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=6
        )
        user_entry = ttk.Entry(form_frame, textvariable=self.login_user_var, width=30)
        user_entry.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(form_frame, text="Password").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=6
        )
        password_entry = ttk.Entry(
            form_frame,
            textvariable=self.login_password_var,
            show="*",
            width=30
        )
        password_entry.grid(row=1, column=1, sticky="ew", pady=6)

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 2))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(
            button_frame,
            text="Login",
            command=self.login_user
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(
            button_frame,
            text="Register",
            command=self.register_user
        ).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(
            button_frame,
            text="Reconnect",
            command=self.reconnect_to_server
        ).grid(row=0, column=2, sticky="ew", padx=(6, 0))

        ttk.Label(
            self.login_frame,
            textvariable=self.connection_text
        ).grid(row=3, column=0, pady=(14, 4))

        self.login_result_label = ttk.Label(
            self.login_frame,
            textvariable=self.login_result_text,
            foreground=self.login_result_default_color
        )
        self.login_result_label.grid(row=4, column=0)

        user_entry.bind("<Return>", lambda event: self.login_user())
        password_entry.bind("<Return>", lambda event: self.login_user())

    # Build the main window after login.
    def build_main_frame(self):
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        top_frame = ttk.Frame(self.main_frame, padding=(6, 2))
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top_frame.columnconfigure(3, weight=1)

        ttk.Label(top_frame, textvariable=self.current_user_text).grid(
            row=0, column=0, sticky="w", padx=(0, 18)
        )
        ttk.Label(top_frame, textvariable=self.user_status_text).grid(
            row=0, column=1, sticky="w", padx=(0, 18)
        )
        ttk.Label(top_frame, textvariable=self.connection_text).grid(
            row=0, column=2, sticky="w", padx=(0, 18)
        )
        ttk.Button(
            top_frame,
            text="Refresh",
            command=self.refresh_all_data
        ).grid(row=0, column=4, sticky="e", padx=(0, 8))
        ttk.Button(
            top_frame,
            text="Logout",
            command=self.logout_user
        ).grid(row=0, column=5, sticky="e")

        body_pane = ttk.Panedwindow(self.main_frame, orient=tk.HORIZONTAL)
        body_pane.grid(row=1, column=0, sticky="nsew")

        friends_frame = ttk.LabelFrame(body_pane, text="Friends", padding=10)
        friends_frame.columnconfigure(0, weight=1)
        friends_frame.rowconfigure(1, weight=1)

        ttk.Label(
            friends_frame,
            text="Your friend list with online or offline status."
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        friend_list_frame = ttk.Frame(friends_frame)
        friend_list_frame.grid(row=1, column=0, sticky="nsew")
        friend_list_frame.columnconfigure(0, weight=1)
        friend_list_frame.rowconfigure(0, weight=1)

        self.friend_listbox = tk.Listbox(
            friend_list_frame,
            selectmode=tk.EXTENDED,
            exportselection=False,
            height=18
        )
        self.friend_listbox.grid(row=0, column=0, sticky="nsew")

        friend_scrollbar = ttk.Scrollbar(
            friend_list_frame,
            orient="vertical",
            command=self.friend_listbox.yview
        )
        friend_scrollbar.grid(row=0, column=1, sticky="ns")
        self.friend_listbox.config(yscrollcommand=friend_scrollbar.set)

        ttk.Label(
            friends_frame,
            text="Friend ID"
        ).grid(row=2, column=0, sticky="w", pady=(10, 4))
        ttk.Entry(
            friends_frame,
            textvariable=self.friend_id_var
        ).grid(row=3, column=0, sticky="ew")

        friend_button_frame = ttk.Frame(friends_frame)
        friend_button_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        friend_button_frame.columnconfigure(0, weight=1)
        friend_button_frame.columnconfigure(1, weight=1)

        ttk.Button(
            friend_button_frame,
            text="Add",
            command=self.add_friend
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(
            friend_button_frame,
            text="Delete",
            command=self.delete_friend
        ).grid(row=0, column=1, sticky="ew", padx=4)

        note_label = ttk.Label(
            friends_frame,
            text="You can select one or more friends here and fill receivers in other tabs."
        )
        note_label.grid(row=5, column=0, sticky="w", pady=(10, 0))

        notebook = ttk.Notebook(body_pane)

        body_pane.add(friends_frame, weight=1)
        body_pane.add(notebook, weight=3)

        self.build_message_tab(notebook)
        self.build_broadcast_tab(notebook)
        self.build_file_tab(notebook)
        self.build_inbox_tab(notebook)

    # Build the send message tab.
    def build_message_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=12)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(4, weight=1)

        ttk.Label(
            tab,
            text="Receiver IDs (use comma to separate more than one friend)"
        ).grid(row=0, column=0, sticky="w")

        recipients_frame = ttk.Frame(tab)
        recipients_frame.grid(row=1, column=0, sticky="ew", pady=(4, 10))
        recipients_frame.columnconfigure(1, weight=1)
        ttk.Button(
            recipients_frame,
            text="Use Selected Friends",
            command=self.fill_message_recipients
        ).grid(row=0, column=0, padx=(0, 8))
        ttk.Entry(
            recipients_frame,
            textvariable=self.message_recipients_var
        ).grid(row=0, column=1, sticky="ew")

        # Show one short hint so first-time users know how this button works.
        ttk.Label(
            tab,
            text="Tip: select friend(s) from the left friend list, then click this button.",
            foreground="#888888"
        ).grid(row=2, column=0, sticky="w", pady=(0, 10))

        ttk.Label(tab, text="Message").grid(row=3, column=0, sticky="nw")

        message_text_frame = ttk.Frame(tab)
        message_text_frame.grid(row=4, column=0, sticky="nsew", pady=(4, 10))
        message_text_frame.columnconfigure(0, weight=1)
        message_text_frame.rowconfigure(0, weight=1)

        self.message_text = tk.Text(message_text_frame, wrap="word", height=14)
        self.message_text.grid(row=0, column=0, sticky="nsew")

        message_scrollbar = ttk.Scrollbar(
            message_text_frame,
            orient="vertical",
            command=self.message_text.yview
        )
        message_scrollbar.grid(row=0, column=1, sticky="ns")
        self.message_text.config(yscrollcommand=message_scrollbar.set)

        ttk.Button(
            tab,
            text="Send Message",
            command=self.send_message
        ).grid(row=5, column=0, sticky="e")

        notebook.add(tab, text="Send Message")

    # Build the broadcast tab.
    def build_broadcast_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=12)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        ttk.Label(
            tab,
            text="Broadcast message to all friends in your current friend list."
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        broadcast_text_frame = ttk.Frame(tab)
        broadcast_text_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        broadcast_text_frame.columnconfigure(0, weight=1)
        broadcast_text_frame.rowconfigure(0, weight=1)

        self.broadcast_text = tk.Text(broadcast_text_frame, wrap="word", height=16)
        self.broadcast_text.grid(row=0, column=0, sticky="nsew")

        broadcast_scrollbar = ttk.Scrollbar(
            broadcast_text_frame,
            orient="vertical",
            command=self.broadcast_text.yview
        )
        broadcast_scrollbar.grid(row=0, column=1, sticky="ns")
        self.broadcast_text.config(yscrollcommand=broadcast_scrollbar.set)

        ttk.Button(
            tab,
            text="Send Broadcast",
            command=self.send_broadcast
        ).grid(row=2, column=0, sticky="e")

        notebook.add(tab, text="Broadcast")

    # Build the send file tab.
    def build_file_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=12)
        tab.columnconfigure(1, weight=1)

        ttk.Label(
            tab,
            text="Receiver IDs"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))
        recipients_frame = ttk.Frame(tab)
        recipients_frame.grid(row=0, column=1, sticky="ew", pady=(0, 6))
        recipients_frame.columnconfigure(1, weight=1)
        ttk.Button(
            recipients_frame,
            text="Use Selected Friends",
            command=self.fill_file_recipients
        ).grid(row=0, column=0, padx=(0, 8))
        ttk.Entry(
            recipients_frame,
            textvariable=self.file_recipients_var
        ).grid(row=0, column=1, sticky="ew")

        ttk.Label(
            tab,
            text="Tip: select friend(s) from the left friend list, then click this button.",
            foreground="#888888"
        ).grid(row=1, column=1, sticky="w", pady=(0, 6))

        ttk.Label(
            tab,
            text="Text file path"
        ).grid(row=2, column=0, sticky="w", pady=6)
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=2, column=1, sticky="ew", pady=6)
        file_frame.columnconfigure(0, weight=1)

        ttk.Entry(
            file_frame,
            textvariable=self.file_path_var
        ).grid(row=0, column=0, sticky="ew")
        ttk.Button(
            file_frame,
            text="Browse",
            command=self.choose_text_file
        ).grid(row=0, column=1, padx=(8, 0))

        info_label = ttk.Label(
            tab,
            text="Only .txt files are allowed. You can type a path or browse for a file."
        )
        info_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 12))

        ttk.Button(
            tab,
            text="Send File",
            command=self.send_file
        ).grid(row=4, column=1, sticky="e")

        notebook.add(tab, text="Send File")

    # Build the inbox tab.
    def build_inbox_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=12)
        tab.columnconfigure(0, minsize=300)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)

        ttk.Label(tab, text="Inbox items").grid(row=0, column=0, sticky="w")
        ttk.Label(tab, text="Item content").grid(row=0, column=1, sticky="w")

        inbox_list_frame = ttk.Frame(tab)
        inbox_list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        inbox_list_frame.columnconfigure(0, weight=1)
        inbox_list_frame.rowconfigure(0, weight=1)

        self.inbox_listbox = tk.Listbox(
            inbox_list_frame,
            exportselection=False,
            height=18
        )
        self.inbox_listbox.grid(row=0, column=0, sticky="nsew")

        inbox_scrollbar = ttk.Scrollbar(
            inbox_list_frame,
            orient="vertical",
            command=self.inbox_listbox.yview
        )
        inbox_scrollbar.grid(row=0, column=1, sticky="ns")
        self.inbox_listbox.config(yscrollcommand=inbox_scrollbar.set)

        inbox_button_frame = ttk.Frame(inbox_list_frame)
        inbox_button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        inbox_button_frame.columnconfigure(0, weight=1)
        ttk.Button(
            inbox_button_frame,
            text="Delete",
            command=self.delete_inbox_item
        ).grid(row=0, column=0, sticky="ew")

        content_frame = ttk.Frame(tab)
        content_frame.grid(row=1, column=1, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        self.inbox_content_text = tk.Text(
            content_frame,
            wrap="word",
            height=18,
            state="disabled"
        )
        self.inbox_content_text.grid(row=0, column=0, sticky="nsew")

        content_scrollbar = ttk.Scrollbar(
            content_frame,
            orient="vertical",
            command=self.inbox_content_text.yview
        )
        content_scrollbar.grid(row=0, column=1, sticky="ns")
        self.inbox_content_text.config(yscrollcommand=content_scrollbar.set)

        self.inbox_listbox.bind(
            "<Double-Button-1>",
            lambda event: self.read_inbox_item()
        )

        notebook.add(tab, text="Inbox")

    # Show the login screen and hide the main screen.
    def show_login_frame(self):
        self.main_frame.grid_forget()
        self.login_frame.grid(row=0, column=0, sticky="nsew")

    # Show the main screen and hide the login screen.
    def show_main_frame(self):
        self.login_frame.grid_forget()
        self.main_frame.grid(row=0, column=0, sticky="nsew")

    # Update the labels that show user and connection state.
    def update_top_labels(self):
        if self.current_user_id == "":
            self.current_user_text.set("Current user: -")
            self.user_status_text.set("User status: offline")
        else:
            self.current_user_text.set("Current user: " + self.current_user_id)
            self.user_status_text.set("User status: online")

    # Show one simple line in the bottom status bar.
    def set_status(self, message):
        self.status_text.set(message)

    # Show one message on the login screen using a normal text color.
    def set_login_result_message(self, message):
        self.login_result_text.set(message)
        self.login_result_label.configure(foreground=self.login_result_default_color)

    # Show one error message on the login screen using a dark red color.
    def set_login_result_error(self, message):
        self.login_result_text.set(message)
        self.login_result_label.configure(foreground=self.login_result_error_color)

    # Update the connection text shown on both screens.
    def set_connection_text(self, is_connected):
        if is_connected:
            text = "Connected to " + config.CLIENT_HOST + ":" + str(config.PORT)
        else:
            text = "Not connected to server"

        self.connection_text.set(text)

    # Connect to the current message server.
    def connect_to_server(self):
        self.close_socket()

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((config.CLIENT_HOST, config.PORT))
            client.receive_reply(self.client_socket)
            self.set_connection_text(True)
            self.set_status("Connected to server.")
            self.set_login_result_message("")
            return True
        except Exception as e:
            self.client_socket = None
            self.set_connection_text(False)
            self.set_login_result_error("Connection failed: " + str(e))
            self.set_status("Connection failed: " + str(e))
            return False

    # Close the current socket if it exists.
    def close_socket(self):
        if self.client_socket is None:
            return

        try:
            self.client_socket.close()
        except:
            pass

        self.client_socket = None

    # Reconnect to the server and return to log in mode.
    def reconnect_to_server(self):
        was_logged_in = self.current_user_id != ""
        self.current_user_id = ""
        self.update_top_labels()
        self.show_login_frame()
        self.clear_main_text_boxes()

        if self.connect_to_server():
            if was_logged_in:
                self.set_login_result_error(
                    "Reconnected. Please login again because the old session has ended."
                )

    # Try to send one request safely.
    def safe_send_command(self, command):
        if self.client_socket is None:
            if not self.connect_to_server():
                return None

        try:
            return client.send_command(self.client_socket, command)
        except Exception as e:
            self.handle_connection_error(e)
            return None

    # Handle a broken connection in one place.
    def handle_connection_error(self, error):
        self.close_socket()
        self.current_user_id = ""
        self.update_top_labels()
        self.set_connection_text(False)
        self.show_login_frame()
        self.clear_main_text_boxes()
        self.set_login_result_error("Connection lost: " + str(error))
        self.set_status("Connection lost: " + str(error))

    # Read a normal OK or ERROR reply.
    def parse_simple_reply(self, reply, command):
        if reply is None:
            return False, "No response from server"

        parts = protocol.parse_message(reply)

        if len(parts) >= 3 and parts[1] == command:
            return parts[0] == "OK", parts[2]

        return False, "Invalid response from server"

    # Login by using the current backend protocol.
    def login_user(self):
        user_id = self.login_user_var.get().strip().lower()
        password = self.login_password_var.get().strip()

        if user_id == "" or password == "":
            self.set_login_result_error("User ID and password cannot be empty.")
            self.set_status("Login failed.")
            return

        request = protocol.build_login_request(user_id, password)
        reply = self.safe_send_command(request)
        login_ok, login_message = self.parse_simple_reply(reply, "LOGIN")

        if login_ok:
            self.current_user_id = user_id
            self.update_top_labels()
            self.show_main_frame()
            self.login_password_var.set("")
            self.set_login_result_message("Login successful.")
            self.refresh_all_data()
            self.set_status(login_message)
        else:
            self.set_login_result_error(login_message)
            self.set_status("Login failed: " + login_message)

    # Register one new account by using the current backend protocol.
    def register_user(self):
        user_id = self.login_user_var.get().strip().lower()
        password = self.login_password_var.get().strip()

        if user_id == "" or password == "":
            self.set_login_result_error("User ID and password cannot be empty.")
            self.set_status("Register failed.")
            return

        request = protocol.build_register_request(user_id, password)
        reply = self.safe_send_command(request)
        register_ok, register_message = self.parse_simple_reply(reply, "REGISTER")

        if register_ok:
            self.login_user_var.set("")
            self.login_password_var.set("")
            self.set_login_result_message("")
            messagebox.showinfo("Register", "Register success, please login again.")
            self.set_status("Register successful: " + register_message)
        else:
            self.set_login_result_error(register_message)
            self.set_status("Register failed: " + register_message)

    # Logout from the server and return to the login screen.
    def logout_user(self):
        if self.current_user_id == "":
            self.show_login_frame()
            return

        if not messagebox.askyesno("Logout", "Do you want to logout now?"):
            return

        reply = self.safe_send_command("LOGOUT")
        logout_ok, logout_message = self.parse_simple_reply(reply, "LOGOUT")

        self.current_user_id = ""
        self.update_top_labels()
        self.show_login_frame()
        self.clear_main_text_boxes()

        if logout_ok:
            self.set_login_result_message(logout_message)
            self.set_status(logout_message)
        else:
            self.set_login_result_error(logout_message)
            self.set_status("Logout finished locally.")

    # Remove old text content after logout.
    def clear_main_text_boxes(self):
        self.friend_status_list = []
        self.inbox_summary_list = []
        self.friend_listbox.delete(0, tk.END)
        self.inbox_listbox.delete(0, tk.END)
        self.friend_id_var.set("")
        self.message_recipients_var.set("")
        self.file_recipients_var.set("")
        self.file_path_var.set("")
        self.message_text.delete("1.0", tk.END)
        self.broadcast_text.delete("1.0", tk.END)
        self.show_inbox_content("")

    # Get selected friend IDs from the friend list box.
    def get_selected_friend_ids(self):
        selected_ids = []

        for index in self.friend_listbox.curselection():
            if 0 <= index < len(self.friend_status_list):
                selected_ids.append(self.friend_status_list[index]["friend_id"])

        return selected_ids

    # Turn the selected friends into comma separated text.
    def join_selected_friends(self):
        selected_ids = self.get_selected_friend_ids()

        if len(selected_ids) == 0:
            self.set_status("Please select friend(s) from the friend list first.")
            return ""

        return ",".join(selected_ids)

    # Put selected friends into the message receiver input.
    def fill_message_recipients(self):
        text = self.join_selected_friends()

        if text != "":
            self.message_recipients_var.set(text)
            self.set_status("Message receivers filled from the friend list.")

    # Put selected friends into the file receiver input.
    def fill_file_recipients(self):
        text = self.join_selected_friends()

        if text != "":
            self.file_recipients_var.set(text)
            self.set_status("File receivers filled from the friend list.")

    # Turn comma separated IDs into a clean list.
    def parse_recipient_text(self, text):
        recipient_list = []

        for part in text.split(","):
            user_id = part.strip().lower()

            if user_id == "":
                continue
            if user_id in recipient_list:
                continue

            recipient_list.append(user_id)

        return recipient_list

    # Refresh both the friend list and inbox list together.
    def refresh_all_data(self):
        if self.current_user_id == "":
            return

        friend_ok, friend_message = self.refresh_friend_list(show_status=False)
        inbox_ok, inbox_message = self.refresh_inbox_list(show_status=False)

        if friend_ok and inbox_ok:
            self.set_status("Friend list and inbox refreshed.")
            return

        error_message_list = []

        if not friend_ok and friend_message != "":
            error_message_list.append("Friend list: " + friend_message)
        if not inbox_ok and inbox_message != "":
            error_message_list.append("Inbox: " + inbox_message)

        if len(error_message_list) > 0:
            self.set_status(" | ".join(error_message_list))

    # Ask the server for the newest friend status list.
    def refresh_friend_list(self, show_status=True):
        if self.current_user_id == "":
            return False, "Please log in first."

        try:
            friend_status_list, error_message = client.get_friend_status_list_from_server(
                self.client_socket, self.current_user_id
            )
        except Exception as e:
            self.handle_connection_error(e)
            return False, str(e)

        if friend_status_list is None:
            if show_status:
                self.set_status("Friend list error: " + error_message)
            return False, error_message

        self.friend_status_list = friend_status_list
        self.friend_listbox.delete(0, tk.END)

        for friend_status in friend_status_list:
            text = friend_status["friend_id"] + " [" + friend_status["status"] + "]"
            self.friend_listbox.insert(tk.END, text)

        if show_status:
            if len(friend_status_list) == 0:
                self.set_status("Friend list refreshed. No friends yet.")
            else:
                self.set_status("Friend list refreshed.")

        return True, ""

    # Add one friend by using the current backend protocol.
    def add_friend(self):
        if self.current_user_id == "":
            return

        friend_id = self.friend_id_var.get().strip().lower()

        if friend_id == "":
            self.set_status("Friend ID cannot be empty.")
            return

        request = protocol.build_add_friend_request(self.current_user_id, friend_id)
        reply = self.safe_send_command(request)
        add_ok, add_message = self.parse_simple_reply(reply, "ADD_FRIEND")

        if add_ok:
            self.friend_id_var.set("")
            self.refresh_friend_list()

        self.set_status(add_message)

    # Delete one friend by using the current backend protocol.
    def delete_friend(self):
        if self.current_user_id == "":
            return

        friend_id = self.friend_id_var.get().strip().lower()

        if friend_id == "":
            selected_ids = self.get_selected_friend_ids()

            if len(selected_ids) == 1:
                friend_id = selected_ids[0]

        if friend_id == "":
            self.set_status("Please enter or select one friend ID first.")
            return

        if not messagebox.askyesno("Delete Friend", "Delete friend " + friend_id + "?"):
            return

        request = protocol.build_delete_friend_request(self.current_user_id, friend_id)
        reply = self.safe_send_command(request)
        delete_ok, delete_message = self.parse_simple_reply(reply, "DELETE_FRIEND")

        if delete_ok:
            self.friend_id_var.set("")
            self.refresh_friend_list()

        self.set_status(delete_message)

    # Send one message to one or more friends.
    def send_message(self):
        if self.current_user_id == "":
            return

        recipient_list = self.parse_recipient_text(self.message_recipients_var.get())
        message_content = self.message_text.get("1.0", tk.END).strip()

        if len(recipient_list) == 0:
            self.set_status("Please enter at least one receiver.")
            return
        if message_content == "":
            self.set_status("Message cannot be empty.")
            return

        request = protocol.build_send_message_request(
            self.current_user_id,
            recipient_list,
            message_content
        )
        reply = self.safe_send_command(request)
        send_ok, send_message_text = self.parse_simple_reply(reply, "SEND_MESSAGE")

        if send_ok:
            self.message_text.delete("1.0", tk.END)

        self.set_status(send_message_text)

    # Send one broadcast to all current friends.
    def send_broadcast(self):
        if self.current_user_id == "":
            return

        message_content = self.broadcast_text.get("1.0", tk.END).strip()

        if message_content == "":
            self.set_status("Broadcast message cannot be empty.")
            return

        request = protocol.build_broadcast_request(
            self.current_user_id,
            message_content
        )
        reply = self.safe_send_command(request)
        send_ok, send_message_text = self.parse_simple_reply(reply, "BROADCAST")

        if send_ok:
            self.broadcast_text.delete("1.0", tk.END)

        self.set_status(send_message_text)

    # Open a normal file chooser for text files.
    def choose_text_file(self):
        file_path = filedialog.askopenfilename(
            title="Choose Text File",
            initialdir=config.BASE_DIR,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path != "":
            self.file_path_var.set(file_path)
            self.set_status("File selected: " + os.path.basename(file_path))

    # Read one text file from the local computer.
    def read_text_file(self, file_path):
        if file_path == "":
            return None, None, "File path cannot be empty"
        if not file_path.lower().endswith(".txt"):
            return None, None, "Only text files are allowed"
        if not os.path.isfile(file_path):
            return None, None, "File does not exist"

        try:
            file = open(file_path, "r")
            file_content = file.read()
            file.close()
        except:
            return None, None, "Cannot read file"

        if file_content.strip() == "":
            return None, None, "File content cannot be empty"

        return os.path.basename(file_path), file_content, ""

    # Send one text file to one or more friends.
    def send_file(self):
        if self.current_user_id == "":
            return

        recipient_list = self.parse_recipient_text(self.file_recipients_var.get())

        if len(recipient_list) == 0:
            self.set_status("Please enter at least one receiver.")
            return

        file_name, file_content, error_message = self.read_text_file(
            self.file_path_var.get().strip()
        )

        if error_message != "":
            self.set_status(error_message)
            return

        request = protocol.build_send_file_request(
            self.current_user_id,
            recipient_list,
            file_name,
            file_content
        )
        reply = self.safe_send_command(request)
        send_ok, send_message_text = self.parse_simple_reply(reply, "SEND_FILE")

        if send_ok:
            self.file_path_var.set("")

        self.set_status(send_message_text)

    # Ask the server for the newest inbox list.
    def refresh_inbox_list(self, show_status=True):
        if self.current_user_id == "":
            return False, "Please log in first."

        try:
            summary_list, error_message = client.get_inbox_list_from_server(
                self.client_socket, self.current_user_id
            )
        except Exception as e:
            self.handle_connection_error(e)
            return False, str(e)

        if summary_list is None:
            if show_status:
                self.set_status("Inbox error: " + error_message)
            return False, error_message

        self.inbox_summary_list = summary_list
        self.inbox_listbox.delete(0, tk.END)

        for i in range(len(summary_list)):
            item_text = str(i + 1) + ". " + summary_list[i]
            self.inbox_listbox.insert(tk.END, item_text)

        if len(summary_list) == 0:
            self.show_inbox_content("Your inbox is empty.")
            if show_status:
                self.set_status("Inbox refreshed. No items.")
        else:
            self.show_inbox_content("Select one inbox item and click Read.")
            if show_status:
                self.set_status("Inbox refreshed.")

        return True, ""

    # Show inbox content in the right text area.
    def show_inbox_content(self, text):
        self.inbox_content_text.config(state="normal")
        self.inbox_content_text.delete("1.0", tk.END)
        self.inbox_content_text.insert("1.0", text)
        self.inbox_content_text.config(state="disabled")

    # Build a simple display text for one inbox item.
    def build_inbox_item_text(self, item_data):
        lines = []

        if item_data["type"] == "message":
            lines.append("Message from " + item_data["sender"])
            lines.append("")
            lines.append("Content")
        elif item_data["type"] == "broadcast":
            lines.append("Broadcast from " + item_data["sender"])
            lines.append("")
            lines.append("Content")
        elif item_data["type"] == "file":
            lines.append("File from " + item_data["sender"])
            lines.append("File name: " + item_data["detail_1"])
            lines.append("")
            lines.append("File content")
        elif item_data["type"] == "acknowledgement":
            lines.append("Acknowledgement from " + item_data["sender"])
            if item_data["detail_1"] == "file" and item_data["detail_2"] != "":
                lines.append("File name: " + item_data["detail_2"])
            lines.append("")
            lines.append("Content")
        else:
            lines.append("Inbox item from " + item_data["sender"])
            lines.append("")
            lines.append("Content")

        lines.append(item_data["content"])
        return "\n".join(lines)

    # Read one selected inbox item from the server.
    def read_inbox_item(self):
        if self.current_user_id == "":
            return

        selected_index_list = self.inbox_listbox.curselection()

        if len(selected_index_list) == 0:
            self.set_status("Please select one inbox item first.")
            return

        item_number = selected_index_list[0] + 1

        try:
            item_data, error_message = client.read_inbox_item_from_server(
                self.client_socket, self.current_user_id, item_number
            )
        except Exception as e:
            self.handle_connection_error(e)
            return

        if item_data is None:
            self.set_status("Read item error: " + error_message)
            return

        self.show_inbox_content(self.build_inbox_item_text(item_data))
        self.set_status("Inbox item loaded.")

    # Delete one selected inbox item from the server.
    def delete_inbox_item(self):
        if self.current_user_id == "":
            return

        selected_index_list = self.inbox_listbox.curselection()

        if len(selected_index_list) == 0:
            self.set_status("Please select one inbox item first.")
            return

        item_number = selected_index_list[0] + 1

        if not messagebox.askyesno("Delete Item", "Delete the selected inbox item?"):
            return

        try:
            delete_ok, delete_message = client.delete_inbox_item_from_server(
                self.client_socket, self.current_user_id, item_number
            )
        except Exception as e:
            self.handle_connection_error(e)
            return

        if delete_ok:
            self.refresh_inbox_list()

        self.set_status(delete_message)

    # Close the socket and the whole program window.
    def close_program(self):
        self.close_socket()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = GuiClientApp(root)
    app.update_top_labels()
    root.mainloop()


if __name__ == "__main__":
    main()
