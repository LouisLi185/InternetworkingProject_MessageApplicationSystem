# Message Application System

This project is a socket-based messaging system written in Python for the INT3069 group project. It uses a simple client-server design over TCP and stores project data in JSON files. The system supports login, friend management, direct messaging, broadcast messaging, text file sending, inbox access, item deletion, and read acknowledgement handling.

The codebase is intentionally kept simple and beginner-friendly. It uses plain Python functions, dictionaries, lists, JSON storage, and a basic line-based text protocol so that the project is easy to read, explain, and demonstrate.

## Main Features

- User login with predefined accounts
- Friend list management
  - View friends
  - Add a friend
  - Delete a friend
- Message module
  - Send a message to one or more friends
  - Support single-line and multi-line messages
- Broadcast module
  - Send one message to all friends of the current user
- File module
  - Send `.txt` files only
  - Send to one friend or multiple friends
  - Check file existence before sending
- Inbox module
  - List messages, broadcasts, files, and acknowledgements
  - Read one selected inbox item
  - Delete one selected inbox item
- Acknowledgement mechanism
  - Reading a normal message sends an acknowledgement to the original sender
  - Reading a file sends an acknowledgement to the original sender
  - Reading an acknowledgement does not create another acknowledgement

## Project Structure

```text
INT3069_GroupProject/
├── src/
│   ├── client.py
│   ├── server.py
│   ├── protocol.py
│   ├── storage.py
│   └── config.py
├── data/
│   ├── default_users.json
│   └── server_data.json
├── text_files/
│   ├── sample1.txt
│   ├── sample2.txt
│   └── sample3.txt
├── docs/
│   └── Protocol_Specification.docx
└── README.md
```

## File Description

### `src/client.py`

The client program handles:

- login
- menu display
- user input
- sending requests to the server
- receiving server replies
- showing messages in a simple boxed text UI

### `src/server.py`

The server program handles:

- TCP connection setup
- request parsing
- login validation
- friend checking
- message, broadcast, and file delivery
- inbox listing, reading, and deleting
- automatic acknowledgement creation

### `src/protocol.py`

This file defines the text-based application protocol used between the client and server. The current implementation uses a simple `|`-separated command format with escaped special characters for multi-line content.

### `src/storage.py`

This file manages all JSON storage logic, including:

- loading user accounts
- loading server data
- saving updated server data
- friend list storage
- message storage
- file storage
- inbox access
- acknowledgement creation

### `src/config.py`

This file stores the basic project configuration:

- server host
- server port
- buffer size
- file paths for JSON data files

### `data/default_users.json`

This file stores the predefined user accounts used for login.

### `data/server_data.json`

This file stores the server-side project data, including:

- friend lists
- message mailboxes
- file mailboxes

### `text_files/`

This folder contains sample `.txt` files for testing the file module.

### `docs/Protocol_Specification.docx`

This folder contains the project protocol document prepared for the course project documentation.

## Requirements

- Python 3
- No external libraries are required

This project uses only the Python standard library, mainly:

- `socket`
- `threading`
- `json`
- `os`

## How to Run

Open two terminals in the project folder.

### 1. Start the server

```bash
python3 src/server.py
```

### 2. Start the client

```bash
python3 src/client.py
```

You can open more client terminals if you want to test different users.

## Default Login Accounts

All default users currently use the same password:

- Password: `1234`

Example user IDs:

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

## Current Modules

### 1. Friend Management

The system supports:

- viewing the current friend list
- adding a valid user as a friend
- deleting an existing friend

### 2. Direct Message Module

The system supports:

- sending a message to one friend or multiple friends
- checking that recipients are in the sender's friend list
- multi-line message input

Multi-line input ends when the user enters two blank lines in a row.

### 3. Broadcast Module

The system supports:

- sending one message to all friends of the current user
- rejecting broadcast if the user has no friends
- storing the broadcast in each friend's message mailbox

### 4. File Module

The system supports:

- sending `.txt` files only
- selecting one or more recipients
- checking that recipients are friends
- checking that the file exists
- reading file content and storing it on the server

The client looks for the entered file name in:

1. `text_files/`
2. the project base folder

### 5. Inbox Module

The inbox supports:

- listing all messages, broadcasts, files, and acknowledgements
- reading one selected item
- deleting one selected item

Inbox items are shown in a numbered list so the user can select them easily.

### 6. Acknowledgement Mechanism

The system supports automatic acknowledgements:

- When a normal message is read, an acknowledgement is sent to the original sender
- When a file is read, an acknowledgement is sent to the original sender
- When an acknowledgement is read, no new acknowledgement is created

This prevents acknowledgement loops.

## Protocol Style

The current project implementation uses a simple plain-text protocol over TCP.

Examples:

```text
LOGIN|jimmy|1234
VIEW_FRIENDS|jimmy
SEND_MESSAGE|jimmy|mary,peter|hello
BROADCAST|jimmy|hello everyone
SEND_FILE|jimmy|mary|sample1.txt|file_content
LIST_INBOX|jimmy
READ_ITEM|jimmy|1
DELETE_ITEM|jimmy|1
```

For multi-line message and file content, the project escapes special characters so that one request can still be sent as one complete text line.

## Data Storage Design

The project stores all server data in `data/server_data.json`.

Top-level structure:

```json
{
    "friends": {},
    "messages": {},
    "files": {}
}
```

### Messages mailbox

Examples of message-related item types:

- `message`
- `broadcast`
- `acknowledgement`

### Files mailbox

Files are stored in the `files` section with fields such as:

- `type`
- `sender`
- `recipients`
- `file_name`
- `content`

## Sample Text Files

The project includes ready-to-use testing files:

- `text_files/sample1.txt`
  - short single-line text
- `text_files/sample2.txt`
  - short multi-line text
- `text_files/sample3.txt`
  - longer multi-line text

These are useful for testing:

- file existence checking
- text file delivery
- file content reading
- multi-line file content preservation

## Notes About the Current Implementation

- The system uses one request and one response per line
- The server keeps data in JSON instead of a database
- The UI is terminal-based and uses a simple boxed display style
- The project is designed to be clear and easy for students to explain in class

## Possible Future Improvements

If the project is extended later, possible directions include:

- stronger password handling
- user registration
- timestamps for inbox items
- inbox sorting
- permanent session handling
- better file type checking
- improved concurrent access protection for JSON updates

## Authors

- Li Haolin 11536573
- Lam Chun Kit 11540512
- Liu Chenghao 11536559
