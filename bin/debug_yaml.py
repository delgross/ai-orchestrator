import yaml
from pathlib import Path

p = Path("ai/config/config.yaml")
try:
    with open(p, "r") as f:
        data = yaml.safe_load(f)
    servers = data.get("mcp_servers", {})
    print(f"Found {len(servers)} servers in config.yaml:")
    print(list(servers.keys()))
except Exception as e:
    print(f"Error: {e}")
