# Message Application System

This project is a Python TCP socket messaging system built for the INT3069 group project. It uses a central threaded server, JSON files for persistence, a simple line-based application protocol, and two clients:

- `src/client.py`: menu-driven CLI client
- `src/gui_client.py`: Tkinter GUI client

The final version keeps the original beginner-friendly structure while adding practical improvements for demonstration:

- user registration
- online or offline friend status
- a GUI client with reconnect support
- chunked file transfer in the GUI client
- optional compression for larger text payloads
- SHA-256 integrity verification
- progress feedback during GUI file transfer

## Authors

- Li Haolin 11536573
- Lam Chun Kit 11546512
- Liu Chenghao 11536559

## What the System Supports

- login and logout
- register a new account
- view friend list
- view friend online or offline status
- add a friend
- delete a friend
- send a direct message to one or more friends
- broadcast a message to all current friends
- send `.txt` files to one or more friends
- list inbox items
- read inbox items
- delete inbox items
- automatically generate read acknowledgements for direct messages and files

## Current Project Layout

```text
INT3069_GroupProject/
├── README.md
├── data/
│   ├── default_users.json
│   └── server_data.json
├── docs/
│   ├── INT3069_GroupProject_Report.pdf
│   ├── INT3069_GroupProject_Report.tex
│   ├── references.bib
│   └── figures/
│       ├── .gitkeep
│       ├── gui_login.png
│       └── gui_main.png
├── src/
│   ├── client.py
│   ├── config.py
│   ├── gui_client.py
│   ├── protocol.py
│   ├── server.py
│   └── storage.py
├── text_files/
│   ├── sample1.txt
│   ├── sample2.txt
│   └── sample3.txt
└── video/
    └── .gitkeep
```

## File Overview

### Runtime source files

`src/config.py`

- stores host, port, buffer size, chunk size, compression threshold, and data file paths

`src/protocol.py`

- defines the plain-text request and response protocol
- escapes and restores message or file text
- builds and parses both the original commands and the chunked transfer commands
- handles Base64 conversion, checksum creation, compression preparation, and payload restoration

`src/storage.py`

- reads and writes `data/default_users.json`
- reads and writes `data/server_data.json`
- prepares empty storage for users
- stores friend lists, messages, files, inbox summaries, and acknowledgements

`src/server.py`

- listens for TCP connections
- handles one client per thread
- validates login, registration, and command ownership
- manages online user counts for presence display
- stores messages and files
- rebuilds chunked GUI file transfers before saving them

`src/client.py`

- provides the CLI workflow
- uses menu-based interaction
- supports multiline message input
- keeps the older simple `SEND_FILE` path
- reads files from `text_files/` first, then from the project root

`src/gui_client.py`

- provides the Tkinter GUI workflow
- supports login, register, reconnect, logout, refresh, messaging, broadcast, file transfer, and inbox viewing
- uses the newer chunked transfer path for files
- shows transfer summary text, percentage, and a progress bar

### Data files

`data/default_users.json`

- stores user IDs and passwords
- currently contains 10 default accounts:
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
- all default passwords are `1234`
- newly registered users are also written here

`data/server_data.json`

- stores three top-level sections:
  - `friends`
  - `messages`
  - `files`
- the current repository copy is reset to a clean demo state with empty lists for the default users

### Sample files

`text_files/sample1.txt`

- a short single-line sample file

`text_files/sample2.txt`

- a multiline sample text file

`text_files/sample3.txt`

- a much larger text file for chunking, compression, and progress-bar demos

### Documentation files

`docs/INT3069_GroupProject_Report.tex`

- the tracked English report source for the current project write-up

`docs/INT3069_GroupProject_Report.pdf`

- the compiled report PDF

`docs/references.bib`

- BibTeX references used by the tracked report

`docs/figures/gui_login.png`
`docs/figures/gui_main.png`

- screenshots used in the report

`video/.gitkeep`

- placeholder so the `video/` directory exists in the repository

## Requirements

### Python runtime

- Python 3
- no third-party Python packages

The implementation uses only standard library modules, mainly:

- `socket`
- `threading`
- `json`
- `os`
- `time`
- `base64`
- `hashlib`
- `zlib`
- `tkinter`

### Optional document tools

If you want to rebuild the tracked report in `docs/`, you will need:

- `pdflatex`
- `bibtex`

## Configuration

Default network and transfer settings are defined in `src/config.py`:

```python
SERVER_HOST = "0.0.0.0"
CLIENT_HOST = "127.0.0.1"
PORT = 12345
BUFFER_SIZE = 1024
TRANSFER_CHUNK_SIZE = 700
COMPRESSION_THRESHOLD = 256
```

Meaning:

- `SERVER_HOST = "0.0.0.0"` lets the server accept connections from other machines
- `CLIENT_HOST = "127.0.0.1"` points clients to the same computer by default
- files at or above `256` bytes are compressed before GUI chunk transfer
- the Base64 payload is split into chunks of up to `700` characters

If you want to test across different computers on the same network:

1. keep `SERVER_HOST = "0.0.0.0"` on the machine running the server
2. change `CLIENT_HOST` in `src/config.py` on the client machine to the server machine's IP address
3. make sure the selected port is open and unused

## How to Run

Open the project folder in separate terminals.

### 1. Start the server

```bash
python3 src/server.py
```

### 2. Start a client

CLI client:

```bash
python3 src/client.py
```

GUI client:

```bash
python3 src/gui_client.py
```

You can open multiple clients at the same time to test communication between different users.

## Recommended Demo Flow

The GUI client is the best way to demonstrate the final version.

1. Start `src/server.py`.
2. Open two GUI clients.
3. Log in as two different users.
4. Add friends as needed.
5. Click `Refresh` to reload friend status and inbox state.
6. Send a normal message.
7. Send a broadcast message.
8. Send `text_files/sample1.txt`.
9. Send `text_files/sample3.txt` to demonstrate chunking and compression.
10. Read the received inbox items and check the acknowledgement behavior.

## Client Behavior Notes

### CLI client

- login, registration, logout, friend management, messaging, file sending, and inbox operations are all menu-driven
- multiline message input ends when the user enters two blank lines in a row
- file sending accepts only `.txt` files
- file lookup checks `text_files/` first, then the project root
- inbox items are selected by number
- the CLI client still uses the simple `SEND_FILE` request path

### GUI client

- the login view supports `Login`, `Register`, and `Reconnect`
- the top bar shows current user, user status, and connection state
- the `Refresh` button reloads both friend list and inbox
- friend list selection can be copied into message or file receiver fields with `Use Selected Friends`
- the file tab accepts only `.txt` files
- the GUI file path can be typed manually or selected with a file chooser
- inbox items are opened by double-click
- file sending shows a transfer summary, percentage, and progress bar
- reconnect drops the old local session and returns to the login screen

## Data Model and Rules

### Friend relationships

- friendship is one-way in the current implementation
- if `A` adds `B`, `B` is not automatically added back to `A`

### Inbox ordering

- inbox entries are built from saved messages first and files second
- acknowledgements are stored inside the message box

### Read acknowledgements

- reading a direct message creates an acknowledgement for the original sender
- reading a file creates an acknowledgement for the original sender
- broadcast items do not create acknowledgements
- acknowledgement items do not create more acknowledgements

### Broadcast behavior

- broadcast does not send to every account in the system
- it sends to all friends currently listed under the sender

## Actual Protocol Summary

The running implementation uses a simple plain-text protocol over TCP. Each request or response is one line, and most fields are separated by `|`.

Message and file text are escaped before sending so the protocol can safely carry:

- `|`
- `\`
- newlines

### Core request examples

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

### Chunked GUI file-transfer requests

```text
TRANSFER_START|jimmy|mary|file|jimmy_1776238528767|sample3.txt|5|1|checksum_value
TRANSFER_CHUNK|jimmy|jimmy_1776238528767|file|1|5|chunk_data
TRANSFER_CHUNK|jimmy|jimmy_1776238528767|file|2|5|chunk_data
```

### Response examples

```text
OK|LOGIN|Welcome, jimmy
ERROR|LOGIN|Invalid user ID or password
OK|TRANSFER_START|Ready to receive 5 chunk(s)
OK|TRANSFER_CHUNK|Chunk 1 of 5 received
OK|TRANSFER_CHUNK|File sent successfully
```

## How the Enhanced GUI File Transfer Works

The GUI file workflow is:

1. read a local text file
2. encode the content as UTF-8 bytes
3. compress it with `zlib` if it reaches the configured threshold
4. calculate a SHA-256 checksum on the transfer bytes
5. Base64-encode the transfer payload
6. split the Base64 text into chunks
7. send `TRANSFER_START`
8. send `TRANSFER_CHUNK` requests one by one
9. let the server reassemble the chunks in memory
10. verify the checksum
11. decompress if needed
12. decode back to normal text
13. save the final file content in the normal inbox storage format

This keeps the transport enhancement separate from the saved JSON structure.

