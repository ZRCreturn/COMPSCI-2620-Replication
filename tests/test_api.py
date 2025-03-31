from collections import defaultdict, deque
import json
import tempfile
import os
import pytest
from common.utils import save_to_file, load_from_file
from common.message import Chatmsg

@pytest.fixture
def sample_messages():
    msg1 = Chatmsg(
        sender="Alice",
        recipient="Bob",
        content="Hi Bob!",
        msg_id="m1",
        timestamp=1700000000.0,
        status="unread"
    )

    msg2 = Chatmsg(
        sender="Bob",
        recipient="Alice",
        content="Hey Alice!",
        msg_id="m2",
        timestamp=1700000001.0,
        status="unread"
    )

    return {
        "m1": msg1,
        "m2": msg2
    }

def test_save_and_load_overwrite(sample_messages):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name

    try:
        # Save to file using overwrite
        save_to_file(sample_messages, filename, mode='overwrite')

        # Prepare data structures for loading
        message_store = {}
        messages = defaultdict(lambda: defaultdict(deque))

        # Load back
        load_from_file(message_store, messages, filename)

        # Assertions
        assert set(message_store.keys()) == set(sample_messages.keys())
        for msg_id, msg in message_store.items():
            original = sample_messages[msg_id]
            assert msg.sender == original.sender
            assert msg.recipient == original.recipient
            assert msg.content == original.content
            assert msg.id in messages[msg.recipient][msg.sender]

    finally:
        os.remove(filename)


def test_save_append_and_delete(sample_messages):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name

    try:
        # Save first message with overwrite
        save_to_file({"m1": sample_messages["m1"]}, filename, mode='overwrite')

        # Append second message
        save_to_file(sample_messages["m2"], filename, mode='append')

        # Append delete operation for m1
        save_to_file(["m1"], filename, mode='delete')

        # Load back
        message_store = {}
        messages = defaultdict(lambda: defaultdict(deque))
        load_from_file(message_store, messages, filename)

        # Only m2 should remain
        assert "m1" not in message_store
        assert "m2" in message_store
        msg = message_store["m2"]
        assert msg.content == "Hey Alice!"
        assert msg.id in messages[msg.recipient][msg.sender]

    finally:
        os.remove(filename)
