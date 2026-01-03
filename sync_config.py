import yaml
import requests
import os
from pathlib import Path

# Load Config
config_path = Path("config/config.yaml")
with open(config_path, "r") as f:
    cfg = yaml.safe_load(f)

agent_model = cfg.get("agent_runner", {}).get("model")
print(f"Disk Request: {agent_model}")

if agent_model:
    # Sync to API
    payload = {
        "agent_model": agent_model
    }
    try:
        res = requests.post("http://localhost:5460/admin/llm/roles", json=payload)
        print(f"API Sync Result: {res.status_code} - {res.json()}")
    except Exception as e:
        print(f"Failed to sync: {e}")
