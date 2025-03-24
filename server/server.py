import socket
import sys
import threading
import time
from server.handler import client_thread_entry, message_store, messages, node_name
from common.utils import load_from_file, save_to_file
import signal
from server.config_loader import ServerConfig, parse_cli_args
from server.grpc_sync import run_grpc_server
from server.grpc_client import SyncClient


def signal_handler(sig, frame):
    print("\nCtrl+C pressed. Exiting...")
    sys.exit(0)
    
def start_server():
    # Parse command-line arguments
    args = parse_cli_args()
    try:
        config = ServerConfig(args.config)
        current_node = config.get_current_node(args.node)
        print(f"🚀 Starting node {args.node} ({current_node.get('desc')})")
 
        tcp_host = current_node["tcp"]["host"]
        tcp_port = current_node["tcp"]["port"]
        grpc_port = current_node["grpc"]["port"]
        node_name[0] = current_node['name']

        # start grpc server for sync  
        grpc_thread = threading.Thread(
            target=run_grpc_server,
            args=(grpc_port,),
            daemon=True
        )
        grpc_thread.start()

        # create sync client 
        peer_addrs = config.get_peer_grpc_addrs(args.node) 
        peer_nodes = config.get_peer_nodes(args.node)
        peer_info = [f"{n['address']} ({n['desc']})" for n in peer_nodes]
        sync_client = SyncClient(peer_addrs)
        # sync message from other nodes
        load_from_file(message_store, messages, f'{node_name[0]}.json')
        print(f"🔄 Syncing with peer nodes: {', '.join(peer_info)}")
        # sleep 3s to let other nodes' grpc server start
        time.sleep(3)
        sync_client.sync_on_startup(message_store)
        save_to_file(message_store, f'{node_name[0]}.json', 'overwrite')

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((tcp_host, tcp_port))
        server_socket.listen(5)
        print(f"🟢 Server listening on {tcp_host}:{tcp_port}")
        while True:
            client_socket, addr = server_socket.accept()
            t = threading.Thread(target=client_thread_entry, args=(client_socket, addr))
            t.start()

    except Exception as e:
        # Handle startup failure
        print(f"⛔ Startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    start_server()
