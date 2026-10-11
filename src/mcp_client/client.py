import json
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

MCP_JSON_FILE = Path("mcp.json")

def get_mcp_server_config() -> dict:
    default_mcp_configs = {}
    if MCP_JSON_FILE.exists():
        try:
            with MCP_JSON_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "mcpServers" in data:
                    return data["mcpServers"]
                elif isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"Warning: Failed to load {MCP_JSON_FILE} ({e})")
            return default_mcp_configs
    return default_mcp_configs

# Initialize client with parsed configurations
client = MultiServerMCPClient(get_mcp_server_config())