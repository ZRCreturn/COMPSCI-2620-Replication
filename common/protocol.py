import struct
from common.message import Chatmsg

class Protocol:
    # constant for message type
    # request
    REQ_LOGIN_1 = 1
    REQ_LOGIN_2 = 2
    REQ_SEND_MSG = 3
    REQ_READ_MSG = 4
    REQ_LIST_MESSAGES = 5
    REQ_LIST_USERS = 6
    REQ_DELETE_MESSAGE = 7
    REQ_DELETE_ACCOUNT = 8
    REQ_PING = 9

    # response
    RESP_USER_EXISTING = 101
    RESP_USER_NOT_EXISTING = 102
    RESP_LOGIN_SUCCESS = 103
    RESP_LOGIN_FAILED = 104
    RESP_LIST_MESSAGES = 105
    RESP_LIST_USERS = 106

    @staticmethod
    def encode_obj(obj):
        """
        Serialize Python objects to binary format.
        """
        if isinstance(obj, int):
            return b'\x00' + struct.pack('!q', obj)

        elif isinstance(obj, float):
            return b'\x01' + struct.pack('!d', obj)  # 8-byte float

        elif isinstance(obj, str):
            data = obj.encode('utf-8')
            length = len(data)
            return b'\x02' + struct.pack('!I', length) + data

        elif isinstance(obj, list):
            encoded_items = [Protocol.encode_obj(item) for item in obj]
            return b'\x03' + struct.pack('!I', len(obj)) + b''.join(encoded_items)

        elif isinstance(obj, dict):
            encoded_items = []
            for k, v in obj.items():
                encoded_key = Protocol.encode_obj(str(k))
                encoded_value = Protocol.encode_obj(v)
                encoded_items.append(encoded_key + encoded_value)
            return b'\x04' + struct.pack('!I', len(obj)) + b''.join(encoded_items)

        elif isinstance(obj, Chatmsg):
            # Define Chatmsg as type 0x04, then encode it as a dictionary
            encoded_chatmsg = Protocol.encode_obj(obj.to_dict())
            return b'\x05' + encoded_chatmsg

        else:
            raise TypeError(f"Unsupported type: {type(obj)}")

    @staticmethod
    def decode_obj(data, offset=0):
        """
        Deserialize binary data back to Python objects.
        """
        type_code = data[offset]
        offset += 1

        if type_code == 0x00:
            (val,) = struct.unpack_from('!q', data, offset)
            offset += 8
            return val, offset

        elif type_code == 0x01:
            (val,) = struct.unpack_from('!d', data, offset) 
            offset += 8
            return val, offset

        elif type_code == 0x02:
            (str_len,) = struct.unpack_from('!I', data, offset)
            offset += 4
            s = data[offset:offset + str_len].decode('utf-8')
            offset += str_len
            return s, offset

        elif type_code == 0x03:
            (list_size,) = struct.unpack_from('!I', data, offset)
            offset += 4
            arr = []
            for _ in range(list_size):
                item, offset = Protocol.decode_obj(data, offset)
                arr.append(item)
            return arr, offset

        elif type_code == 0x04:
            (dict_size,) = struct.unpack_from('!I', data, offset)
            offset += 4
            d = {}
            for _ in range(dict_size):
                key, offset = Protocol.decode_obj(data, offset)
                value, offset = Protocol.decode_obj(data, offset)
                d[key] = value
            return d, offset

        elif type_code == 0x05:
            # Decode dictionary first, then convert to Chatmsg
            chatmsg_dict, offset = Protocol.decode_obj(data, offset)
            return Chatmsg.from_dict(chatmsg_dict), offset

        else:
            raise ValueError(f"Unknown type code: {type_code}")

