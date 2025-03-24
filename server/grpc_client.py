import grpc
from generated.sync_pb2 import DataPackage, MessageData, Empty
from generated.sync_pb2_grpc import DataSyncStub
from common.message import Chatmsg

class SyncClient:
    def __init__(self, target_nodes):
        self.channels = [
            grpc.insecure_channel(addr) for addr in target_nodes
        ]
        self.stubs = [DataSyncStub(ch) for ch in self.channels]
        self.stubs_addr = {}
        for i in range(len(self.stubs)):
            self.stubs_addr[self.stubs[i]]= target_nodes[i]

    def fetch_full_data(self):
        """Fetch full data from the first available node"""
        for stub in self.stubs:
            try:
                return stub.GetFullData(Empty())
            except grpc.RpcError as e:
                print(f"Failed to fetch data from node {self.stubs_addr[stub]}: {e}")
        raise Exception("All nodes are unavailable")

    def sync_on_startup(self, local_data):
        """Perform synchronization on startup"""
        try:
            remote_data = self.fetch_full_data()
            for remote_msg in remote_data.messages:
                id = remote_msg.id
                if id not in local_data or remote_msg.timestamp > local_data[id].timestamp:
                    local_data[id] = Chatmsg(
                        sender=remote_msg.sender,
                        recipient=remote_msg.recipient,
                        content=remote_msg.content,
                        msg_id=remote_msg.id,
                        status=remote_msg.status,
                        timestamp=remote_msg.timestamp
                    )
            return 
        except Exception as e:
            print(f"⛔ Startup synchronization failed: {e}")
            return 

    def full_sync(self, data_package):
        for stub in self.stubs:
            try:
                stub.FullSync(data_package)
            except grpc.RpcError as e:
                print(f"Full sync failed to {self.stubs_addr[stub]}: {e}")

    def incremental_sync(self, data_package):
        for stub in self.stubs:
            try:
                stub.IncrementalSync(data_package)
            except grpc.RpcError as e:
                print(f"Incremental sync failed to {self.stubs_addr[stub]}: {e}")

    def create_data_package(self, new_msgs=[], deleted_ids=[], read_ids=[]):
        return DataPackage(
            messages=[self._convert_message(m) for m in new_msgs],
            deleted_ids=deleted_ids,
            read_ids = read_ids
        )

    def _convert_message(self, msg):
        return MessageData(
            id=msg.id,
            sender=msg.sender,
            recipient=msg.recipient,
            content=msg.content,
            status=msg.status,
            timestamp=msg.timestamp
        )
