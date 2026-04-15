# Message Application System

This project is a socket-based messaging system written in Python for the INT3069 group project. It uses a central TCP server, JSON files for persistence, a simple line-based application protocol, and two client interfaces:

- a terminal client in `src/client.py`
- a Tkinter GUI client in `src/gui_client.py`

The current version keeps the original beginner-friendly project style and adds two practical networking enhancements for the GUI file workflow:

- chunked transfer with integrity checking
- compression for larger text file payloads

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
- GUI file transfer progress display
- Chunked file transfer in the GUI client
- Compression for larger file payloads
- SHA-256 integrity verification after transfer reassembly

## Current Project Structure

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
├── FINAL_PROJECT_DOCUMENTATION_ZH_TW.tex
├── FINAL_PROJECT_REFERENCES.bib
├── FINAL_PROJECT_DOCUMENTATION_ZH_TW.pdf
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
- supports both the old `SEND_FILE` path and the newer chunked transfer path
- reassembles incoming transfer chunks
- verifies SHA-256 integrity checks
- decompresses transferred data when needed
- writes persistent changes to `data/server_data.json`

### `src/client.py`

The terminal client:

- shows text menus
- sends protocol requests to the server
- supports login and registration
- supports multi-line message input
- supports file sending from `text_files/` or the project root
- shows inbox items in a boxed terminal layout

The terminal client keeps the original simple file-sending path and does not use the GUI progress-bar workflow.

### `src/gui_client.py`

The GUI client:

- provides a Tkinter desktop interface
- supports login, registration, reconnect, and logout
- shows friend status in a left-side list
- supports message, broadcast, file, and inbox workflows in tabs
- uses one top `Refresh` button to reload both friend list and inbox
- opens inbox items by double-click
- keeps a simple inbox layout with one `Delete` button under the list
- sends files through the newer chunked transfer workflow
- shows a small transfer info label, percentage text, and progress bar for file sending

### `src/protocol.py`

This file defines the actual protocol used by the running system:

- plain text
- one request or response per line
- `|` as the main field separator
- escaped special characters for multi-line text and file content
- helper functions for chunked transfer
- helper functions for compression and decompression
- helper functions for SHA-256 checksums

It includes both:

- the original command builders such as `LOGIN`, `SEND_MESSAGE`, `SEND_FILE`
- the newer transfer commands `TRANSFER_START` and `TRANSFER_CHUNK`

### `src/storage.py`

This file handles:

- reading and writing JSON data
- preparing empty server data for users
- friend storage
- message storage
- file storage
- inbox listing and deletion
- acknowledgement creation

The storage format is intentionally kept simple. Chunking and compression happen only during transfer, not in the saved JSON structure.

### `src/config.py`

This file stores:

- server host
- client host
- port
- buffer size
- transfer chunk size
- compression threshold
- JSON file paths

Current transfer-related settings:

```python
TRANSFER_CHUNK_SIZE = 700
COMPRESSION_THRESHOLD = 256
```

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
- `sample3.txt`: large text file for bigger transfer tests, chunking tests, and compression demos

### `docs/Protocol_Specification.docx`

This file is a course documentation artifact. It is not an exact description of the current implementation.

The document describes a JSON and token-based protocol, while the actual code in `src/` uses a plain-text line protocol with `|` separators and does not use session tokens.

### Root documentation files

These files explain the final version of the project:

- `FINAL_PROJECT_DOCUMENTATION_ZH_TW.tex`
- `FINAL_PROJECT_REFERENCES.bib`
- `FINAL_PROJECT_DOCUMENTATION_ZH_TW.pdf`

They are for report and presentation use, not for running the system itself.

## Running Requirements

### Python application

- Python 3
- No third-party Python libraries

The messaging system uses only the standard library, mainly:

- `socket`
- `threading`
- `json`
- `os`
- `tkinter`
- `base64`
- `hashlib`
- `time`
- `zlib`

### Optional document build tools

If you want to rebuild the final PDF documentation, the LaTeX files were prepared for:

- `pdfLaTeX`
- `BibTeX`

## Configuration

Default connection settings are defined in `src/config.py`:

```python
SERVER_HOST = "0.0.0.0"
CLIENT_HOST = "127.0.0.1"
PORT = 12345
BUFFER_SIZE = 1024
TRANSFER_CHUNK_SIZE = 700
COMPRESSION_THRESHOLD = 256
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
- The terminal client keeps the original simple `SEND_FILE` request path.

### GUI client

- The login screen supports `Login`, `Register`, and `Reconnect`.
- Login-screen errors are shown in dark red.
- After successful registration, the GUI shows a message box and asks the user to log in again.
- The top `Refresh` button reloads both the friend list and inbox.
- The inbox opens items by double-click.
- The file tab supports only `.txt` files.
- The file tab shows transfer information, percentage, and a progress bar.
- The GUI file workflow uses chunked transfer with optional compression.

## Actual Protocol Summary

The running implementation uses a simple line-based request and response protocol.

Examples of the original command style:

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

Examples of the newer GUI transfer path:

```text
TRANSFER_START|jimmy|mary|file|jimmy_1776238528767|sample3.txt|5|1|checksum_value
TRANSFER_CHUNK|jimmy|jimmy_1776238528767|file|1|5|chunk_data
TRANSFER_CHUNK|jimmy|jimmy_1776238528767|file|2|5|chunk_data
```

Server responses follow the same simple style:

```text
OK|LOGIN|Welcome, jimmy
ERROR|LOGIN|Invalid user ID or password
OK|TRANSFER_START|Ready to receive 5 chunk(s)
OK|TRANSFER_CHUNK|Chunk 1 of 5 received
OK|TRANSFER_CHUNK|File sent successfully
```

## How the Enhanced File Transfer Works

The newer GUI file transfer workflow is:

1. read the text file
2. convert it into UTF-8 bytes
3. compress it with `zlib` if it reaches the configured threshold
4. calculate a SHA-256 checksum on the transferred bytes
5. Base64-encode the payload into text
6. split the encoded text into chunks
7. send `TRANSFER_START`
8. send `TRANSFER_CHUNK` messages one by one
9. let the server reassemble the chunks
10. verify the checksum
11. decompress if needed
12. save the final normal file content in the inbox

This design keeps the saved JSON data simple while still demonstrating application-layer protocol enhancement.

## Notes About Current Repository State

- `server_data.json` is currently cleared for a clean demo start.
- The GUI is the main demonstration client for the final version.
- The CLI client remains available and compatible with the simpler workflow.
- The root LaTeX and PDF files are documentation outputs, not required for runtime.

## Optional LaTeX Build Commands

If you want to rebuild the Chinese final documentation PDF:

```bash
pdflatex -interaction=nonstopmode FINAL_PROJECT_DOCUMENTATION_ZH_TW.tex
bibtex FINAL_PROJECT_DOCUMENTATION_ZH_TW
pdflatex -interaction=nonstopmode FINAL_PROJECT_DOCUMENTATION_ZH_TW.tex
pdflatex -interaction=nonstopmode FINAL_PROJECT_DOCUMENTATION_ZH_TW.tex
```
