import grpc
import time
import threading
from concurrent import futures
import pytest

from collections import defaultdict
from google.protobuf.empty_pb2 import Empty
from generated import sync_pb2, sync_pb2_grpc

# ---------- Mock Storage and Utilities ----------

message_store = {}
messages = defaultdict(lambda: defaultdict(list))
node_name = ["test_node"]

class Chatmsg:
    def __init__(self, sender, recipient, content, msg_id, status, timestamp):
        self.id = msg_id
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.status = status
        self.timestamp = timestamp

def save_to_file(data, filename, mode="append"):
    # Mocked: no real file I/O
    pass

# ---------- gRPC Service Implementation ----------

class SyncService(sync_pb2_grpc.DataSyncServicer):
    def FullSync(self, request, context):
        message_store.clear()
        messages.clear()
        for msg_data in request.messages:
            self._add_message(msg_data)

        for msg_id in request.deleted_ids:
            self._remove_message(msg_id)
        
        save_to_file(message_store, f'{node_name[0]}.json', mode='overwrite')
        return sync_pb2.SyncResponse(success=True)

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

        return sync_pb2.SyncResponse(success=True)

    def GetFullData(self, request, context):
        return sync_pb2.DataPackage(
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
        return sync_pb2.MessageData(
            id=msg.id,
            sender=msg.sender,
            recipient=msg.recipient,
            content=msg.content,
            status=msg.status,
            timestamp=msg.timestamp
        )

# ---------- gRPC Test Fixtures and Client ----------

@pytest.fixture(scope="module")
def grpc_test_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sync_pb2_grpc.add_DataSyncServicer_to_server(SyncService(), server)
    port = server.add_insecure_port('[::]:50551')
    server.start()
    print(f"Test gRPC server started on port {port}")
    time.sleep(1)
    yield
    server.stop(0)

@pytest.fixture
def grpc_stub(grpc_test_server):
    channel = grpc.insecure_channel('localhost:50551')
    stub = sync_pb2_grpc.DataSyncStub(channel)
    return stub

# ---------- Test Cases ----------

def test_full_sync(grpc_stub):
    message_store.clear()
    messages.clear()

    msg1 = sync_pb2.MessageData(
        id="m1", sender="alice", recipient="bob", content="Hello", status="sent", timestamp=time.time()
    )
    msg2 = sync_pb2.MessageData(
        id="m2", sender="carol", recipient="bob", content="Hi", status="sent", timestamp=time.time()
    )

    request = sync_pb2.DataPackage(messages=[msg1, msg2], deleted_ids=["doesnotexist"])
    resp = grpc_stub.FullSync(request)
    assert resp.success
    assert "m1" in message_store and "m2" in message_store

def test_incremental_sync_add_and_read(grpc_stub):
    new_msg = sync_pb2.MessageData(
        id="m3", sender="dave", recipient="bob", content="Yo", status="sent", timestamp=time.time()
    )
    request = sync_pb2.DataPackage(messages=[new_msg], read_ids=["m1"])
    resp = grpc_stub.IncrementalSync(request)
    assert resp.success
    assert "m3" in message_store
    assert message_store["m1"].status == "read"

def test_incremental_sync_delete(grpc_stub):
    assert "m2" in message_store
    request = sync_pb2.DataPackage(deleted_ids=["m2"])
    resp = grpc_stub.IncrementalSync(request)
    assert resp.success
    assert "m2" not in message_store

def test_get_full_data(grpc_stub):
    resp = grpc_stub.GetFullData(Empty())
    ids = {m.id for m in resp.messages}
    assert "m1" in ids
    assert "m3" in ids
    assert "m2" not in ids

def test_full_sync_overwrites_existing(grpc_stub):
    # Add initial message
    original = sync_pb2.MessageData(
        id="m100", sender="x", recipient="y", content="Original", status="sent", timestamp=time.time()
    )
    grpc_stub.FullSync(sync_pb2.DataPackage(messages=[original]))

    # Overwrite it
    updated = sync_pb2.MessageData(
        id="m100", sender="x", recipient="y", content="Updated", status="delivered", timestamp=time.time()
    )
    grpc_stub.FullSync(sync_pb2.DataPackage(messages=[updated]))

    assert message_store["m100"].content == "Updated"
    assert message_store["m100"].status == "delivered"

def test_incremental_sync_duplicate_id(grpc_stub):
    dup_msg = sync_pb2.MessageData(
        id="m1", sender="alice", recipient="bob", content="Updated Hello", status="read", timestamp=time.time()
    )
    grpc_stub.IncrementalSync(sync_pb2.DataPackage(messages=[dup_msg]))

    # Should overwrite the original "m1"
    assert message_store["m1"].content == "Updated Hello"
    assert message_store["m1"].status == "read"

def test_incremental_delete_nonexistent_id(grpc_stub):
    assert "fake_id" not in message_store
    resp = grpc_stub.IncrementalSync(sync_pb2.DataPackage(deleted_ids=["fake_id"]))
    assert resp.success  # Should not crash

def test_incremental_read_nonexistent_id(grpc_stub):
    resp = grpc_stub.IncrementalSync(sync_pb2.DataPackage(read_ids=["no_such_msg"]))
    assert resp.success  # Should silently skip

def test_get_full_data_when_empty(grpc_stub):
    # Clear everything
    grpc_stub.FullSync(sync_pb2.DataPackage(messages=[], deleted_ids=[]))
    resp = grpc_stub.GetFullData(Empty())
    assert len(resp.messages) == 0

def test_incremental_sync_empty_payload(grpc_stub):
    resp = grpc_stub.IncrementalSync(sync_pb2.DataPackage())
    assert resp.success  # Should be handled gracefully
