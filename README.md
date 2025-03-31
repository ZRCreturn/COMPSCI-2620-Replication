# COMPSCI-2620-Wire-Protocols

This project implements a basic socket-based chat server that supports multiple clients, user account creation, login, message sending, offline message storage, and more. It is built in Python using the `socket` library and `threading` for concurrency.

## Overview

The server accepts incoming TCP connections from clients, handles user authentication, and processes various chat-related requests (like sending or reading messages). The code uses a custom binary protocol to encode and decode messages. User credentials are hashed using BCrypt for secure password storage.

### Main Components

- **server.py**  
  Main entry point of the chat server. Starts listening for incoming connections, spawns a dedicated thread to handle each client’s requests.

- **handler.py**  
  Provides logic to handle client requests. It manages user login, message sending, message reading, listing messages, and deleting accounts.

- **message.py**  
  Defines the `Chatmsg` class, representing individual chat messages with attributes like ID, sender, recipient, content, timestamp, and status.

- **protocol.py**  
  Implements the `Protocol` class that encodes and decodes various data types (strings, lists, dictionaries, custom objects like `Chatmsg`) into a binary format for sending over the network.

- **utils.py**  
  Contains helper methods for receiving data from the socket, sending data, hashing passwords, and verifying passwords.

- **gui.py**    
  Implements the client frontend using Tkinter and socket programming. The GUI allows a user to log in, send and receive messages, view a list of users, and delete messages or their account.



## message defination
This is the design plan from the design phase, and there may be some minor differences from the final implemented version.
```
general message:
    int64       msg_type = xxx
    uint32      data_len = length of payload
    # above is 12 bytes
    bytes       payload  = serialized obj

login_usrname:
    msg_type = 1
    data_len = length of payload
    payload = user_name

login_pwd:
    msg_type = 2
    data_len = length of payload
    payload = user_pwd

...

# we could define msg_type >= 100 as reply message
reply_error:
    msg_type = 100
    data_len = length of payload
    payload = error_msg

reply_create_account:
    msg_type = 101
    data_len = 0
    payload = null
...
```

## server design 
below is the framework(pseudocode) of how the server works
```
Class Server:
    Initialize host and port
    Create a TCP socket, bind to (host, port), and listen for connections

    Method start():
        Loop:
            Accept incoming client connection
            Start a new thread to handle client communication


Class ClientHandler:
    Maintain:
        - connected_clients {address: username}
        - user_accounts {username: password}
        - message_store {msg_id: Message}
        - messages {recipient: {sender: deque([msg_id1, msg_id2, ...])}}

    Method handle(client_socket, address):
        Store client connection info
        Loop:
            Receive (msg_type, parsed_obj)
            If no message, break loop
            Process request based on msg_type
        Close connection

    Method process_request(sock, address, msg_type, parsed_obj):
        Case REQ_LOGIN_
            
        Case REQ_SEND_MSG:

        Case REQ_READ_MSG:

        Case REQ_LIST_MESSAGES:

        Case REQ_LIST_USERS:

        Case REQ_DELETE_MESSAGE:

        Case REQ_DELETE_ACCOUNT:

```

## frontend design 
a pseudocode of how the frontend works
```
Initialization:

- Set up the Tkinter root window.
- Define connection parameters (host, port).
- Initialize the login screen and start the application.

Login Process:

- Username Screen: Display a prompt for the username, and validate it.
- Password Screen: After submitting the username, prompt for a password and validate it.
- If login is successful, move to the user list screen.
- If login fails, display an error message.

User List Screen:

- Fetch a list of users from the server.
- Display a list of users with unread message counts.
- Allow the user to select another user to see messages.

Message List Screen:

- Display messages with options to send a new message or delete existing ones.
- Allow the user to click on a message to delete it.

Account Deletion:

- Provide a button to delete the user's account, which closes the connection.

Helper Methods:

- clear_screen: Removes all widgets from the screen to update UI.
- send_data & recv_data: Communicate with the server by sending and receiving data.

```


## Features

1. **User Registration and Login**  
   - The server prompts new users to create a password when it detects an unregistered username.
   - Existing users are required to enter their password to log in.
   - Passwords are stored in hashed form using BCrypt for security.

2. **Message Sending**  
   - Registered users can send messages to other users.  
   - Messages to offline users are stored until they log in, at which time the server will mark them as delivered.

3. **Reading Messages**  
   - Users can request to read incoming messages from a particular sender.
   - Once read, the server updates the message status.

4. **Message Listing**  
   - Users can list all messages in the conversation between themselves and another user, both sent and received.

5. **Account Deletion**  
   - Users can delete their account. This removes all messages they have sent or received from the server.

6. **Threaded Server**  
   - Each client connection runs in its own thread, allowing multiple clients to interact with the server concurrently.

## Getting Started

### Prerequisites

- **Python 3.9+**  
- **bcrypt** library (for hashing and checking passwords)

Install the required libraries:

```sh
pip install bcrypt
```

### Project Structure

```
project_root/
│── server/
│   ├── server.py          # Entry point for server execution
│   ├── handler.py       # Core logic for handling client requests
│   ├── __init__.py
│
│── common/
│   ├── protocol.py      # Implementation of message protocol encoding & decoding
│   ├── utils.py         # Helper functions for logging, error handling, etc.
│   ├── message.py       # customized class for chat message
│   ├── __init__.py
│
│── gui.py # Client-side entry point
│
│── tests/               # Unit tests
│── README.md            # Project documentation
│── requirements.txt     # Dependencies
```

### Usage

1. **Start the server**  
notice: please add -m as prarmeter of running this python script(also use server.server instead of \server\server.py). this ensures that Python treats the script as a module, searching for it correctly within `sys.path` before executing it
   ```
   python -m  server.server --node=node2 --config=cluster_config.json # this script for windows, param node means the node to be lanuched.
   ```
   This will start the server listening on the addr configed by cluster_config file.
   If you have a public IP or multiple machines on the same local network, you can modify the IP address in the code to your public IP or local network IP. This way, multiple machines can participate in the chat instead of being limited to the local machine.


2. **start the client**  
   ```
   python .\gui.py # this script for windows
   ```

3. **Log in / Create account**  
   - If the user does not exist, the server expects the user to create a password.
   - If the user does exist, you must supply the correct password.

4. **run tests**
   - python -m pytest tests

## Contributing  
- **Ruichen Zhang**: Backend implementation, protocol design, and test suite development.  
- **Kiran Pyles**: Frontend (GUI) implementation.

# -----------------------------------------------------
# Replication project update 
## Fault Tolerance & Persistence

To support crash recovery and data durability, the system introduces the following fault-tolerance features:

### ✅ Append-Only Persistent Storage (JSON)

Instead of storing data only in memory, messages and operations are now logged to a **JSON file** using an append-only format.

- Each operation (send, read, delete) is appended as a new line in the log.
- The file can be replayed during startup to fully rebuild the server state.
- Designed to be efficient and human-readable.

### ✅ Incremental Logging Design

By appending changes instead of overwriting the whole dataset, we gain:

- **Crash safety**: No data is lost during crashes.
- **Better performance**: O(1) writes vs full file rewrites.
- **Traceability**: Easy to debug and inspect logs.
- Future-ready for **log compaction** support.

### ✅ gRPC-Based Server Synchronization

To allow multiple backend servers to synchronize their state:

- A **gRPC service** was introduced for backend-to-backend communication.
- Internal state changes (new message, read status, deletion) are **broadcasted** to peer nodes via gRPC.
- This keeps internal logic (synchronization) **decoupled** from external logic (TCP client communication).
- Enables support for **horizontal scaling** and **high availability**.

### ✅ Cluster Config Loader

A `servers.json` file defines the cluster layout and server roles.

- Easily configure multiple server instances.
- Avoids hardcoding ports and IPs.
- Supports tools like `get_peer_nodes()` to help with sync setup.

