import socket
import sys
import threading
import time
from server.handler import client_thread_entry, message_store, messages
from common.utils import load_from_file
import signal

HOST = '127.0.0.1'
PORT = 5000
def signal_handler(sig, frame):
    print("\nCtrl+C pressed. Exiting...")
    sys.exit(0)
    
def start_server():
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    load_from_file(message_store,messages, 'test.json')

    while True:
        client_socket, addr = server_socket.accept()
        t = threading.Thread(target=client_thread_entry, args=(client_socket, addr))
        t.start()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    start_server()
