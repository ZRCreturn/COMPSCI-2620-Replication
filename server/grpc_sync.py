import grpc
from concurrent import futures
import threading
from generated.sync_pb2 import DataPackage, SyncResponse, MessageData
from generated.sync_pb2_grpc import DataSyncServicer, add_DataSyncServicer_to_server
from server.handler import message_store, messages, lock, node_name
from common.utils import save_to_file
from common.message import Chatmsg

class SyncService(DataSyncServicer):
    def FullSync(self, request, context):
    
        message_store.clear()
        messages.clear()
        for msg_data in request.messages:
            self._add_message(msg_data)

        for msg_id in request.deleted_ids:
            self._remove_message(msg_id)
        
        save_to_file(message_store, f'{node_name[0]}.json', mode='overwrite')
        return SyncResponse(success=True)

    def IncrementalSync(self, request, context):
        if len(request.messages) != 0:
            for msg_data in request.messages:
                msg = self._add_message(msg_data)
                save_to_file(msg, f'{node_name[0]}.json', mode='append')
            
        if len(request.deleted_ids) != 0:
            for id in request.deleted_ids:
                self._remove_message(id)
            save_to_file(list(request.deleted_ids), f'{node_name[0]}.json', mode='delete')

        if len(request.read_ids) != 0:
            for id in request.read_ids:
                self._read_message(id)
            save_to_file(list(request.read_ids), f'{node_name[0]}.json', mode='read')
        
        return SyncResponse(success=True)
    
    def GetFullData(self, request, context):
        return DataPackage(
            messages=[self._convert_message(m) for m in message_store.values()]
        )

    def _add_message(self, msg_data):
        msg = Chatmsg(
            sender=msg_data.sender,
            recipient=msg_data.recipient,
            content=msg_data.content,
            msg_id=msg_data.id,
            status=msg_data.status,
            timestamp=msg_data.timestamp
        )
        message_store[msg.id] = msg
        messages[msg.recipient][msg.sender].append(msg.id)
        return msg
    
    def _remove_message(self, msg_id):
        if msg_id in message_store:
            msg = message_store.pop(msg_id)
            if msg.recipient in messages and msg.sender in messages[msg.recipient]:
                messages[msg.recipient][msg.sender].remove(msg.id)
    
    def _read_message(self, msg_id):
        if msg_id in message_store:
            message_store[msg_id].status = "read"


    def _convert_message(self, msg):
        return MessageData(
            id=msg.id,
            sender=msg.sender,
            recipient=msg.recipient,
            content=msg.content,
            status=msg.status,
            timestamp=msg.timestamp
        )

def run_grpc_server(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DataSyncServicer_to_server(SyncService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"🚀 gRPC sync server started on port {port}")
    server.wait_for_termination()
