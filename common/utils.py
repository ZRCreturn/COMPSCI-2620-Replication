from collections import defaultdict, deque
import json
import struct
import bcrypt
from common.protocol import Protocol
from common.message import Chatmsg

def recv_data(sock):
    # receive 12 bytes header
    header = sock.recv(12)
    if len(header) < 12:
        return None, None

    # parse header
    msg_type, data_len = struct.unpack("!QI", header)

    if data_len == 0:
        return msg_type, None
    
    # read payload
    payload = b""
    while len(payload) < data_len:
        chunk = sock.recv(data_len - len(payload))
        if not chunk:
            return None, None 
        payload += chunk

    obj, _ = Protocol.decode_obj(payload)
    return msg_type, obj

def send_data(sock, msg_type, data):
    if data is None:
        payload = b""
    else:
        payload = Protocol.encode_obj(data)
    data_len = len(payload)
    header = struct.pack('!QI', msg_type, data_len)
    sock.sendall(header + payload)    

def hash_pwd(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()  

def check_pwd(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())    

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Chatmsg):
            return obj.__dict__
        return super().default(obj)

def send_data_json(sock, msg_type, data):
    if data is None:
        payload = b""
    else:
        payload = json.dumps(data, cls=CustomJSONEncoder).encode('utf-8')

    data_len = len(payload)
    header = struct.pack('!QI', msg_type, data_len)
    sock.sendall(header + payload)

def decode_json(obj):
    if isinstance(obj, dict) and "sender" in obj and "message" in obj:
        return Chatmsg(**obj)  
    elif isinstance(obj, list):
        return [decode_json(item) for item in obj] 
    return obj  

def recv_data_json(sock):
    header = sock.recv(12)
    if len(header) < 12:
        return None, None

    msg_type, data_len = struct.unpack("!QI", header)

    if data_len == 0:
        return msg_type, None
    
    payload = b""
    while len(payload) < data_len:
        chunk = sock.recv(data_len - len(payload))
        if not chunk:
            return None, None 
        payload += chunk

    try:
        obj = json.loads(payload.decode('utf-8'))
        obj = decode_json(obj)  
    except json.JSONDecodeError:
        return None, None  

    return msg_type, obj

def save_to_file(data, filename, mode='overwrite'):
    """
    Universal storage function with multiple modes
    :param data: Accepts three data formats:
        1. Full dataset (dictionary format)
        2. Single Chatmsg object
        3. List of message IDs (for batch operations)
    :param filename: Target storage filename
    :param mode: Storage mode - overwrite | append | delete| read
    """
    def _write_entries(f, entries):
        """Helper function to write JSON entries"""
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    # Mode preprocessing
    if mode == 'overwrite':
        file_mode = 'w'
    elif mode in ('append', 'delete', 'read'):
        file_mode = 'a' 
    else:
        raise ValueError(f"Invalid mode: {mode}")

    # Data standardization
    if isinstance(data, dict):  # Full dataset
        entries = [v.to_dict() for v in data.values()]
    elif isinstance(data, Chatmsg):  # Single message
        entries = [data.to_dict()]
    elif isinstance(data, list):  # Batch operation
        if mode == 'delete':
            entries = [{"operation": "delete", "ids": data}]
        elif mode == 'read':
            entries = [{"operation": "read", "ids": data}]
    else:
        raise TypeError("Unsupported data type")

    # Execute storage operation
    with open(filename, file_mode) as f:
        _write_entries(f, entries)


def load_from_file(filename):
    """
    Load chat data from file and populate both data structures
    :param filename: JSON file path to load
    :param message_store: Dict to store messages {msg_id: Chatmsg}
    :param messages: Nested defaultdict for message relationships {recipient: {sender: deque(msg_ids)}}
    """
    # Temporary storage for atomic loading
def load_from_file(message_store, messages, filename):
    try:
        with open(filename, 'r') as f:
            for line in f:
                record = json.loads(line)
                if "operation" in record:
                    if record["operation"] == "delete":
                        for msg_id in record["ids"]:
                            message_store.pop(msg_id, None)
                    if record["operation"] == "read":
                        for msg_id in record["ids"]:
                            message_store[msg_id].status = 'read'
                    continue
                
                msg = Chatmsg.from_dict(record)
                message_store[msg.id] = msg
            
            for msg in message_store.values():
                messages[msg.recipient][msg.sender].append(msg.id)
                
    except FileNotFoundError:
        pass

def save_user_accounts_to_json(user_accounts, filename='user_accounts.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(user_accounts, f, ensure_ascii=False, indent=4)

def load_user_accounts_from_json(user_accounts, filename='user_accounts.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        user_accounts.clear()
        user_accounts.update(data)
    except FileNotFoundError:
        print(f"File {filename} not found. Keeping dictionary empty.")
        user_accounts.clear()
    except json.JSONDecodeError:
        print(f"File {filename} is not valid JSON. Keeping dictionary empty.")
        user_accounts.clear()
