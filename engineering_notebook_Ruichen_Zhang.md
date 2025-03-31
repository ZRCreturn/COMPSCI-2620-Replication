# Engineering Notebook

## February 3: Designing the Message Protocol

Before diving into coding, I believe the most crucial step is to clearly define the communication protocol. Since the client and server communicate via TCP sockets by transmitting byte streams, the core challenge lies in determining the message format.

One of the most elegant concepts in computing is **metadata**, or headers. A good design practice here is to structure every message as **metadata + payload**, where the payload contains the actual data in a byte stream. The metadata should include essential information required by the protocol. 

First, since client-server communication relies purely on sockets—unlike modern web apps that leverage structured APIs—the **message type (msg_type)** must be explicitly defined to distinguish different requests and responses. Second, the metadata should include the **payload length**, making it easier to parse messages efficiently.

Based on this, the final message format is as follows:

```
General Message Structure:
    int64       msg_type  = xxx
    uint32      data_len  = length of payload
    # The above metadata occupies 12 bytes
    bytes       payload   = serialized object

Login Requests:
    msg_type = 1
    data_len = length of payload
    payload = user_name (string)

    msg_type = 2
    data_len = length of payload
    payload = user_password (string)

...

# Define msg_type >= 100 as reply messages
Reply Messages:
    msg_type = 100
    data_len = length of payload
    payload = error_message (string)

    msg_type = 101
    data_len = 0
    payload = null
...
```

---

## February 4: Implementing Serialization & Deserialization

Today, I primarily worked on refining the protocol design, with a key challenge being the serialization and deserialization of transmitted messages. Given Python's flexibility in handling core data types, I decided to implement a **universal encoding and decoding method**. This approach ensures that the system remains extensible regardless of future design changes.

The implementation covers fundamental data types: `int`, `str`, `list`, and `dict`. Given the nature of `list` and `dict`, recursion is the most intuitive way to process them.

The implementation proceeded smoothly, as expected, leveraging recursion:

```python
import struct

def encode_obj(obj):
    """
    Serializes Python objects into a byte stream.
    """
    if isinstance(obj, int):
        # Define int as type 0x00 + 8-byte signed integer
        return b'\x00' + struct.pack('!q', obj)

    elif isinstance(obj, str):
        # Define str as type 0x01 + 4-byte length + UTF-8 encoded byte array
        data = obj.encode('utf-8')
        length = len(data)
        return b'\x01' + struct.pack('!I', length) + data

    elif isinstance(obj, list):
        # Define list as type 0x02 + 4-byte size + encode_obj(elements)
        encoded_items = [encode_obj(item) for item in obj]
        total = b''.join(encoded_items)
        return b'\x02' + struct.pack('!I', len(obj)) + total

    elif isinstance(obj, dict):
        # Define dict as type 0x03 + 4-byte size + encode_obj(key) + encode_obj(value)
        # Keys are required to be strings
        encoded_items = []
        for k, v in obj.items():
            encoded_key = encode_obj(str(k))
            encoded_value = encode_obj(v)
            encoded_items.append(encoded_key + encoded_value)
        total = b''.join(encoded_items)
        return b'\x03' + struct.pack('!I', len(obj)) + total

    else:
        raise TypeError(f"Unsupported type: {type(obj)}")
```

---

## February 5: Designing the Framework

Today, I focused on designing the overall project framework and structuring the file directory. The **server-side** was decomposed into modular components, and a `common` directory was introduced to store shared utilities.

### **Project Structure:**
```
project_root/
│── server/
│   ├── main.py          # Entry point for server execution
│   ├── handler.py       # Core logic for handling client requests
│   ├── config.py        # Server configuration parameters
│   ├── __init__.py
│
│── common/
│   ├── protocol.py      # Implementation of message protocol encoding & decoding
│   ├── utils.py         # Helper functions for logging, error handling, etc.
│   ├── __init__.py
│
│── client/
│   ├── main.py          # Client-side entry point
│   ├── __init__.py
│
│── tests/               # Unit tests
│── README.md            # Project documentation
│── requirements.txt     # Dependencies
```

### **Key Components:**
- **`handler.py`**: Handles incoming messages from clients, dispatching them to the appropriate processing functions.
- **`protocol.py`**: Defines the serialization and deserialization logic for message encoding and decoding.
- **`utils.py`**: Contains utility functions for logging, error handling, and debugging.

that's how I design the framework 
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

### **Next Steps (TODO):**
- Implement the core logic inside `handler.py` to process different message types.
- Finalize the `protocol.py` encoding/decoding implementation.
- Develop the client-side request structure in `request.py`.
- Set up unit tests to validate message transmission.


## February 7: Thoughts on Designing the Login System

When handling user login, a key consideration is managing connections and usernames. In typical web applications, authentication is often handled using JWT tokens or storing session IDs in cookies. However, since this project relies solely on sockets for communication between the client and server, it requires a custom approach to managing and storing connection and account information.

My initial thought is to use a **global map** to maintain the mapping between **connection addresses** and **usernames**. This mapping would be dynamically updated in the following scenarios:
- **When a client connects**: A new entry is created in the map.
- **Upon login**: The username is associated with the connection.
- **Upon logout**: The mapping is removed.
- **When a connection is lost**: The corresponding entry is cleaned up.

This design ensures that the server can efficiently track active users and manage authentication without relying on an external session store.

Today finish most part of the business logic
### **Next Steps (TODO):**
- finish business logic of handling all kinds of message.
- finish test suits


## February 9: Debugging Import Issues in Python

While running the code, I encountered the following error:

```
from server.handler import client_thread_entry
ModuleNotFoundError: No module named 'server.handler'; 'server' is not a package
```

I wasn't entirely clear on Python's import mechanism. I tried adding `__init__.py` and several other fixes, but they didn’t resolve the issue. Eventually, I discovered that running the script with the `-m` flag as a module resolved the problem:

```
python -m server.server
```

This approach ensures that Python treats the script as a module, searching for it correctly within `sys.path` before executing it. The deeper details of Python’s import mechanism are something I'll explore further in the future.

### **Next Steps (TODO):**
- Organize all the code and ensure a clean structure.
- Write documentation for the project.



## February 10: Adding Locks for Global Variable Modification

To ensure thread safety when modifying global variables related to `send`, `read`, and `delete` message operations, I added locks. In Python, thanks to the **context manager**, using locks becomes very **Pythonic**—simply wrapping critical sections with `with lock` ensures proper locking and unlocking.

This approach makes concurrency management much more convenient and readable.


## March 23: Adding Fault Tolerance via Persistence

To make the chat application fault-tolerant, I focused on **introducing persistent storage** to back up in-memory data structures. This step is crucial because all data (such as messages and user mappings) were previously stored in memory, and any server crash would lead to a total loss.

### **Why Not Use a Database?**

One intuitive solution to persistence is integrating a relational or NoSQL database. However, I decided **not to use a full-fledged database system** for several reasons:
- This project is a **lightweight demo**, and introducing a database feels unnecessarily **heavy**.
- A database would **require managing multiple running instances**, which would complicate the setup and **reduce the portability** of the project.
- Theoretically, databases have built-in **master-slave replication**, which could handle fault tolerance at the storage level—but that would offload too much of the core fault tolerance logic to the DB layer, which defeats the educational value of implementing it myself.

### **Why Use JSON?**

After evaluating options, I settled on using **JSON-formatted logs** to persist chat data. The reasons are:
- **Human-readable and lightweight**, suitable for demo and debugging.
- Python's `json` module makes it easy to implement and maintain.

### **Implementation Highlights**

I implemented a generic storage function, `save_to_file()`, which supports various modes including:
- `overwrite`: Save the full dataset
- `append`: Add new messages
- `delete`: Record deletion operations
- `read`: Mark messages as read

Here’s a key snippet from the `save_to_file()` function:

```python
def save_to_file(data, filename, mode='overwrite'):
    ...
    if isinstance(data, dict):  # Full dataset
        entries = [v.to_dict() for v in data.values()]
    elif isinstance(data, Chatmsg):  # Single message
        entries = [data.to_dict()]
    elif isinstance(data, list):  # Batch operations
        if mode == 'delete':
            xxx
        elif mode == 'read':
            xxx
    ...
```
To reconstruct the in-memory state during startup, I added a complementary function, load_from_file(), which reads logs and restores both message_store and messages.

This way, even if the server crashes, the system can recover the full message history and relationships.

## March 24: Designing Append-Only Incremental Persistence

Yesterday I implemented most of the data Persistence work, today I made a important design decision, which is appending changes incrementally for delete and update operations.

### **Why Append Instead of Overwrite?**

1. **Avoid losing data**:  
   If the server crashes, previous data is still safe because we never erase it—we only add new lines.

2. **Faster performance**:  
   Appending a new message takes less time than rewriting the whole file every time.

3. **Easy to understand**:  
   You can open the file and clearly see the history of all operations—message sends, reads, and deletions.

---

### **How Does It Work?**

In the `save_to_file()` function:

- When a user sends a message, we convert it to JSON and **append** it to the file:
```json
{"id": "msg123", "sender": "alice", "recipient": "bob", "content": "...", "status": "unread"}
```

- When a message is read, we add a special entry:
```json
{"operation": "read", "ids": ["msg123"]}
```

- When a message is deleted:
```json
{"operation": "delete", "ids": ["msg123"]}
```

All changes are stored in order, one per line.

---

### **Loading Data Back**

When the server starts, the `load_from_file()` function reads the file **line by line**. It first stores the original messages, then applies the read and delete operations to build the final state in memory.

This way, even after a crash or shutdown, the chat history and message status can be fully restored.

---

✅ **Next Steps:**
- Add support for compacting the log file (snapshot + clean-up)
- Store user accounts in the same way


## March 26: Using gRPC for Backend Server Synchronization

Today, I introduced **gRPC** to handle backend synchronization between multiple server instances. This marks a major step forward in building a **distributed and fault-tolerant chat system**.

### **Why Add Server Synchronization?**

To ensure **high availability** and **data consistency**, multiple server instances must stay in sync. For example, if one server goes down, others should still have the latest message state.

### **Why gRPC?**

Originally, all client-server communication was done using a **custom protocol** over **raw TCP sockets**, sending byte streams back and forth. However, trying to use that same protocol for **server-to-server sync** introduces problems:

- **Too much coupling**: We'd mix internal logic (synchronization) with external-facing logic (client requests).
- **Extra complexity**: We'd have to build a second layer of parsing and routing into the same TCP handler.

By contrast, **gRPC offers a clean separation** of concerns:

- Synchronization is now handled on a separate channel.
- Protobuf definitions make data structures easy to manage.
- Built-in streaming and bi-directional communication fit our sync use case well.

---

### **Current Design**

Each server exposes a gRPC service with methods like:
- `SyncNewMessage`
- `SyncReadStatus`
- `SyncDelete`

When one server changes data, it immediately **broadcasts the change to its peers** via gRPC.

This makes the system **modular**, with well-defined boundaries:
- **TCP channel** for client interaction
- **gRPC channel** for backend replication

---

✅ **Next Steps:**
- Finalize protobuf schema definitions and rpc server.
- Build a test environment with 3 server instances
- Add retry and conflict resolution logic for sync


## March 27: Building a Configuration Loader

Today I completed the **config loader** to manage settings for running multiple chat server nodes in a cluster. This module is responsible for loading and validating `servers.json`, and providing easy access to each node's TCP and gRPC settings.

-

As the system evolves into a **multi-node architecture**, it's important to:

- Avoid hardcoding hostnames, ports, or cluster metadata in the source code
- Dynamically configure how many servers to launch and how they interact
- Allow switching environments (e.g., test vs. production) with zero code change

The JSON config file provides a **single source of truth** about the cluster.


Instead of manually parsing JSON everywhere, I created a reusable class `ServerConfig` that:

- **Loads and validates** the structure of the config file
- **Builds a fast lookup map** of nodes by name
- **Provides helper functions** like:
  - `get_current_node(name)`
  - `get_peer_grpc_addrs(exclude)`
  - `get_peer_nodes(exclude)`

This makes the codebase **cleaner, safer, and more flexible**. If a config field is missing, it fails fast with clear error messages.

---

### **Example Use Case**

Run a node via CLI:
```bash
python -m server.main --node node1 --config servers.json
```

This allows the server to boot up using dynamic config, and also discover its **peer nodes** for gRPC sync.

---