# Message Application System

This project is a socket-based messaging system written in Python for the INT3069 group project. It uses a central TCP server, JSON files for persistence, a simple line-based application protocol, and two client interfaces:

- a terminal client in `src/client.py`
- a Tkinter GUI client in `src/gui_client.py`

## Current Features

- Login with predefined accounts from `data/default_users.json`
- Register a new account and persist it to `data/default_users.json`
- View friend list with online or offline status
- Add a friend
- Delete a friend
- Send direct messages to one or more friends
- Send broadcast messages to all current friends
- Send `.txt` files to one or more friends
- View inbox items
- Read inbox items
- Delete inbox items
- Automatically generate acknowledgements when a normal message or file is read

## Project Structure

```text
INT3069_GroupProject/
├── src/
│   ├── client.py
│   ├── config.py
│   ├── gui_client.py
│   ├── protocol.py
│   ├── server.py
│   └── storage.py
├── data/
│   ├── default_users.json
│   └── server_data.json
├── docs/
│   └── Protocol_Specification.docx
├── text_files/
│   ├── sample1.txt
│   ├── sample2.txt
│   └── sample3.txt
├── video/
│   └── .gitkeep
└── README.md
```

## File Overview

### `src/server.py`

The server:

- accepts TCP connections
- handles one client per thread
- validates login and registration
- manages friend lists
- delivers messages, broadcasts, and files
- lists, reads, and deletes inbox items
- tracks online users for friend status display
- writes persistent changes to `data/server_data.json`

### `src/client.py`

The terminal client:

- shows text menus
- sends protocol requests to the server
- supports login and registration
- supports multi-line message input
- supports file sending from `text_files/` or the project root
- shows inbox items in a boxed terminal layout

### `src/gui_client.py`

The GUI client:

- provides a Tkinter desktop interface
- supports login, registration, reconnect, and logout
- shows friend status in a left-side list
- supports message, broadcast, file, and inbox workflows in tabs
- uses one top `Refresh` button to reload both friend list and inbox
- opens inbox items by double-click
- keeps only a `Delete` button under the inbox list

### `src/protocol.py`

This file defines the actual protocol used by the running system:

- plain text
- one request or response per line
- `|` as the main field separator
- escaped special characters for multi-line text and file content

### `src/storage.py`

This file handles:

- reading and writing JSON data
- preparing empty server data for users
- friend storage
- message storage
- file storage
- inbox listing and deletion
- acknowledgement creation

### `src/config.py`

This file stores:

- server host
- client host
- port
- buffer size
- JSON file paths

### `data/default_users.json`

This file stores login accounts. The project currently starts with 10 default users:

- `jimmy`
- `mary`
- `peter`
- `david`
- `john`
- `george`
- `alice`
- `bob`
- `tom`
- `jane`

All 10 default users use password `1234`.

Newly registered users are also written into this file.

### `data/server_data.json`

This file stores:

- `friends`
- `messages`
- `files`

The current repository data has been reset to a clean demo state for the 10 default users, with empty friend lists and empty inbox data.

### `text_files/`

This folder contains sample `.txt` files for file-sending tests:

- `sample1.txt`: short single-line text
- `sample2.txt`: short multi-line text
- `sample3.txt`: longer multi-line text

### `docs/Protocol_Specification.docx`

This file is a course documentation artifact. It is not an exact description of the current implementation. The document describes a JSON and token-based protocol, while the actual code in `src/` uses a plain-text line protocol with `|` separators.

## Requirements

- Python 3
- No third-party libraries

The project uses only the standard library, mainly:

- `socket`
- `threading`
- `json`
- `os`
- `tkinter`

## Configuration

Default connection settings are defined in `src/config.py`:

```python
SERVER_HOST = "0.0.0.0"
CLIENT_HOST = "127.0.0.1"
PORT = 12345
BUFFER_SIZE = 1024
```

If you want to connect from another computer on the same network:

1. keep `SERVER_HOST = "0.0.0.0"` on the server machine
2. change `CLIENT_HOST` on the client machine to the server machine's IP address
3. make sure the selected port is open and unused

## How to Run

Open the project folder in separate terminals.

### 1. Start the server

```bash
python3 src/server.py
```

### 2. Start one client

Terminal client:

```bash
python3 src/client.py
```

GUI client:

```bash
python3 src/gui_client.py
```

You can open multiple clients at the same time to test communication between different users.

## Usage Notes

### Terminal client

- Login and registration are handled from the terminal menu.
- Multi-line message input ends when the user enters two blank lines in a row.
- File sending checks `text_files/` first, then the project root.
- Inbox items are selected by number.

### GUI client

- The login screen supports `Login`, `Register`, and `Reconnect`.
- Login-screen errors are shown in dark red.
- After successful registration, the GUI shows a message box and asks the user to log in again.
- The top `Refresh` button reloads both the friend list and inbox.
- The inbox opens items by double-click.
- The inbox keeps a single full-width `Delete` button under the list.

## Actual Protocol Summary

The running implementation uses a simple line-based request and response protocol.

Examples:

```text
LOGIN|jimmy|1234
REGISTER|newuser|pass123
VIEW_FRIENDS|jimmy
VIEW_FRIENDS_STATUS|jimmy
ADD_FRIEND|jimmy|mary
DELETE_FRIEND|jimmy|mary
SEND_MESSAGE|jimmy|mary,peter|hello
BROADCAST|jimmy|hello everyone
SEND_FILE|jimmy|mary|sample1.txt|file_content
LIST_INBOX|jimmy
READ_ITEM|jimmy|1
DELETE_ITEM|jimmy|1
LOGOUT
```

Server responses follow the same simple style:

```text
OK|LOGIN|Welcome, jimmy
ERROR|LOGIN|Invalid user ID or password
```

For multi-line messages and file content, special characters are escaped before sending and restored after receiving.

## Data Design

Top-level structure of `data/server_data.json`:

```json
{
    "friends": {},
    "messages": {},
    "files": {}
}
```

### Friend lists

- friend relationships are stored per user as simple lists
- adding a friend is one-directional in the current implementation

### Message box

The `messages` section can contain:

- normal messages
- broadcasts
- acknowledgements

### File box

The `files` section contains file items with fields such as:

- `type`
- `sender`
- `recipients`
- `file_name`
- `content`

### Inbox order

Inbox display is assembled dynamically:

1. all message-box items first
2. all file-box items after that

## Acknowledgement Rules

The server automatically creates acknowledgements when:

- a normal message is read
- a file is read

The server does not create another acknowledgement when:

- a broadcast is read
- an acknowledgement is read
- the item was already acknowledged before

## Important Notes

- The project has both a terminal client and a GUI client.
- Registration is already implemented and persists new users.
- The server rewrites `server_data.json` on startup to ensure all users have `friends`, `messages`, and `files` entries.
- There is no automated test suite in the repository at the moment.
- The Word protocol document should be treated as reference material, not as the exact live protocol contract.

## Authors

- Li Haolin 11536573
- Lam Chun Kit 11540512
- Liu Chenghao 11536559
