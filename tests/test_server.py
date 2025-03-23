import socket
import threading
import time
import pytest
from server.server import start_server, HOST, PORT 
from server.handler import user_accounts, connected_clients
from common.utils import send_data, recv_data
from common.message import Chatmsg
from common.protocol import Protocol


@pytest.fixture(scope="session")
def server():
    """start server thread"""
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)  
    yield


def test_login(server):  
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    send_data(client_socket, Protocol.REQ_LOGIN_1, "test_user")
    resp_type, resp = recv_data(client_socket)
    assert resp_type == Protocol.RESP_USER_NOT_EXISTING

    send_data(client_socket, Protocol.REQ_LOGIN_2, "password")
    resp_type, resp = recv_data(client_socket)
    assert resp_type == Protocol.RESP_LOGIN_SUCCESS
    assert list(user_accounts.keys()) == ["test_user"]

    send_data(client_socket, Protocol.REQ_LOGIN_1, "test_user")
    resp_type, resp = recv_data(client_socket)
    assert resp_type == Protocol.RESP_USER_EXISTING

    send_data(client_socket, Protocol.REQ_LOGIN_2, "fake password")
    resp_type, resp = recv_data(client_socket)
    assert resp_type == Protocol.RESP_LOGIN_FAILED

    send_data(client_socket, Protocol.REQ_LOGIN_2, "password")
    resp_type, resp = recv_data(client_socket)
    assert resp_type == Protocol.RESP_LOGIN_SUCCESS
    assert list(user_accounts.keys()) == ["test_user"]


    client_socket.close()
    time.sleep(0.5)
    assert len(connected_clients) == 0

def test_send_read_list_msg(server):

    # login as eric
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    send_data(client_socket, Protocol.REQ_LOGIN_1, "eric")
    resp_type, resp = recv_data(client_socket)
    send_data(client_socket, Protocol.REQ_LOGIN_2, "password")
    resp_type, resp = recv_data(client_socket)

    
    # eric send bob a message -- hey
    data = ["bob", "hey"]
    send_data(client_socket, Protocol.REQ_SEND_MSG, data)
    # eric list the correspondence between him and bob
    send_data(client_socket, Protocol.REQ_LIST_MESSAGES, "bob")
    resp_type, resp = recv_data(client_socket)
    assert resp_type == Protocol.RESP_LIST_MESSAGES
    # check if messge is expected
    message_hey = resp[0]
    except_message1 = Chatmsg(sender="eric", recipient="bob", content= "hey", status="unread")
    assert message_hey == except_message1


    # eric send bob another message -- second hey
    data = ["bob", "second hey"]
    send_data(client_socket, Protocol.REQ_SEND_MSG, data)
    # request msg list 
    send_data(client_socket, Protocol.REQ_LIST_MESSAGES, "bob")
    resp_type, resp = recv_data(client_socket)
    message_hey = resp[0]
    message_second_hey = resp[1]
    except_message1 = Chatmsg(sender="eric", recipient="bob", content= "hey", status="unread")
    except_message2 = Chatmsg(sender="eric", recipient="bob", content= "second hey", status="unread")
    assert message_hey == except_message1
    assert message_second_hey == except_message2
    # request user list
    send_data(client_socket, Protocol.REQ_LIST_USERS, None)
    resp_type, resp = recv_data(client_socket)
    assert resp == {"eric":0, "test_user" :0}


    # login as bob
    client_socket_bob = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket_bob.connect((HOST, PORT))
    send_data(client_socket_bob, Protocol.REQ_LOGIN_1, "bob")
    resp_type, resp = recv_data(client_socket_bob)
    send_data(client_socket_bob, Protocol.REQ_LOGIN_2, "passwordbob")
    resp_type, resp = recv_data(client_socket_bob)
    # request user list
    send_data(client_socket, Protocol.REQ_LIST_USERS, None)
    resp_type, resp = recv_data(client_socket)
    assert resp == {"eric":0, "test_user" :0, "bob" :0}
    send_data(client_socket_bob, Protocol.REQ_LIST_USERS, None)
    resp_type, resp = recv_data(client_socket_bob)
    assert resp == {"eric":2, "test_user" :0, "bob" :0}
    # bob read unread-message from eric
    send_data(client_socket_bob, Protocol.REQ_READ_MSG, "eric")
    # eric request msg list 
    send_data(client_socket, Protocol.REQ_LIST_MESSAGES, "bob")
    resp_type, resp = recv_data(client_socket)
    message_hey = resp[0]
    message_second_hey = resp[1]
    except_message1 = Chatmsg(sender="eric", recipient="bob", content= "hey", status="read")
    except_message2 = Chatmsg(sender="eric", recipient="bob", content= "second hey", status="read")
    assert message_hey == except_message1
    assert message_second_hey == except_message2
    # now the unread message should be 0
    send_data(client_socket_bob, Protocol.REQ_LIST_USERS, None)
    resp_type, resp = recv_data(client_socket_bob)
    assert resp == {"eric":0, "test_user" :0, "bob" :0}

    # # eric delete message--hey
    # send_data(client_socket, Protocol.REQ_DELETE_MESSAGE, message_hey.id)
    # send_data(client_socket, Protocol.REQ_LIST_MESSAGES, "bob")
    # resp_type, resp = recv_data(client_socket)
    # # check whether message_second_hey is the only message left
    # assert resp[0] == message_second_hey
    # assert len(resp) == 1

    # bob delete his account
    send_data(client_socket_bob, Protocol.REQ_DELETE_ACCOUNT, None)
    send_data(client_socket, Protocol.REQ_LIST_MESSAGES, "bob")
    resp_type, resp = recv_data(client_socket)
    # there should be no message left 
    # assert len(resp) == 0
    send_data(client_socket, Protocol.REQ_LIST_USERS, None)
    resp_type, resp = recv_data(client_socket)
    assert resp == {"eric":0, "test_user" :0}

    client_socket.close()
    client_socket_bob.close()



