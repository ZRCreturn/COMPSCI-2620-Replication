import json
import argparse
from typing import Dict, List

class ServerConfig:
    def __init__(self, config_path: str):
        # Load the configuration file
        with open(config_path) as f:
            self._raw = json.load(f)
        
        # Validate the configuration structure
        self._validate()
        
        # Build a node mapping for quick lookup
        self.nodes = {n["name"]: n for n in self._raw["nodes"]}
    
    def _validate(self):
        # Check if all required fields are present in each node
        required_fields = ["name", "tcp", "grpc"]
        for node in self._raw["nodes"]:
            for field in required_fields:
                if field not in node:
                    raise ValueError(f"Node {node.get('name', 'unknown')} is missing required field: {field}")
    
    def get_current_node(self, node_name: str) -> Dict:
        # Retrieve the configuration of the specified node
        if node_name not in self.nodes:
            raise ValueError(f"Node {node_name} does not exist in the configuration file")
        return self.nodes[node_name]
    
    def get_peer_grpc_addrs(self, exclude: str) -> List[str]:
        """Get the gRPC addresses of other nodes, excluding the specified node."""
        return [
            f"{n['tcp']['host']}:{n['grpc']['port']}"
            for n in self._raw["nodes"]
            if n["name"] != exclude
        ]
    
    def get_peer_nodes(self, exclude: str) -> List[str]:
        """Get the gRPC addresses of other nodes, excluding the specified node."""
        return [
            {
                "address": f"{n['tcp']['host']}:{n['grpc']['port']}",
                "desc": n.get("desc", "no_name_node")
            }
            for n in self._raw["nodes"]
            if n["name"] != exclude
        ]

def parse_cli_args():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Start a chat server node")
    parser.add_argument(
        "--node", 
        required=True,
        help="Name of the node as defined in the configuration file"
    )
    parser.add_argument(
        "--config",
        default="servers.json",
        help="Path to the configuration file (default: servers.json)"
    )
    return parser.parse_args()
