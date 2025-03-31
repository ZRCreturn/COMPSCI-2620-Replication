import pytest
import json
from server.config_loader import ServerConfig

# ---------- Fixtures ----------

@pytest.fixture
def valid_config(tmp_path):
    config_data = {
        "cluster": "chat-cluster-1",
        "nodes": [
            {
                "name": "node1",
                "desc": "main-node",
                "tcp": {"host": "127.0.0.1", "port": 5000},
                "grpc": {"port": 50051},
                "tags": ["primary"]
            },
            {
                "name": "node2",
                "desc": "node-east",
                "tcp": {"host": "127.0.0.1", "port": 5001},
                "grpc": {"port": 50052},
                "tags": ["east"]
            },
            {
                "name": "node3",
                "desc": "node-west",
                "tcp": {"host": "127.0.0.1", "port": 5002},
                "grpc": {"port": 50053},
                "tags": ["west"]
            }
        ]
    }
    path = tmp_path / "valid_config.json"
    with open(path, "w") as f:
        json.dump(config_data, f)
    return str(path)

# ---------- Basic Functionality ----------

def test_config_loads_properly(valid_config):
    cfg = ServerConfig(valid_config)
    assert len(cfg.nodes) == 3
    assert "node2" in cfg.nodes
    assert cfg.nodes["node1"]["tcp"]["port"] == 5000

def test_get_existing_node(valid_config):
    cfg = ServerConfig(valid_config)
    node = cfg.get_current_node("node3")
    assert node["desc"] == "node-west"
    assert node["grpc"]["port"] == 50053

def test_get_nonexistent_node_raises(valid_config):
    cfg = ServerConfig(valid_config)
    with pytest.raises(ValueError, match="does not exist"):
        cfg.get_current_node("nonexistent")

# ---------- gRPC and Peer Nodes ----------

def test_get_peer_grpc_addrs_excludes_self(valid_config):
    cfg = ServerConfig(valid_config)
    peers = cfg.get_peer_grpc_addrs("node1")
    assert "127.0.0.1:50051" not in peers
    assert "127.0.0.1:50052" in peers
    assert "127.0.0.1:50053" in peers

def test_get_peer_nodes_structure(valid_config):
    cfg = ServerConfig(valid_config)
    peers = cfg.get_peer_nodes("node2")
    assert len(peers) == 2
    assert {"address": "127.0.0.1:50051", "desc": "main-node"} in peers
    assert {"address": "127.0.0.1:50053", "desc": "node-west"} in peers

# ---------- Missing Required Fields ----------

@pytest.mark.parametrize("missing_field", ["name", "tcp", "grpc"])
def test_missing_required_fields_raises(tmp_path, missing_field):
    bad_node = {
        "name": "nodeX",
        "tcp": {"host": "127.0.0.1", "port": 6000},
        "grpc": {"port": 6001}
    }
    bad_node.pop(missing_field)
    config_data = {"cluster": "test", "nodes": [bad_node]}
    path = tmp_path / "missing_field.json"
    with open(path, "w") as f:
        json.dump(config_data, f)

    with pytest.raises(ValueError, match=f"missing required field: {missing_field}"):
        ServerConfig(str(path))

# ---------- Edge Cases ----------

def test_empty_nodes_list(tmp_path):
    config_data = {"cluster": "empty", "nodes": []}
    path = tmp_path / "empty_nodes.json"
    with open(path, "w") as f:
        json.dump(config_data, f)
    
    cfg = ServerConfig(str(path))
    assert cfg.nodes == {}

def test_invalid_json_format(tmp_path):
    path = tmp_path / "invalid.json"
    with open(path, "w") as f:
        f.write("{ invalid json }")
    
    with pytest.raises(json.JSONDecodeError):
        ServerConfig(str(path))

def test_file_does_not_exist():
    with pytest.raises(FileNotFoundError):
        ServerConfig("nonexistent_file.json")
