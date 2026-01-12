
import yaml
import asyncio
import httpx
import json
import os

MCP_YAML_PATH = "/Users/bee/Sync/Antigravity/ai/config/mcp.yaml"
DB_URL = "http://127.0.0.1:8000/sql"
DB_NS = "antigravity"
DB_DB = "antigravity"
DB_USER = "root"
DB_PASS = "root"

def load_yaml_config():
    with open(MCP_YAML_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return config.get("mcp_servers", {})

async def migrate_servers():
    servers = load_yaml_config()
    print(f"Found {len(servers)} servers in YAML.")
    
    headers = {
        "Accept": "application/json",
        "NS": DB_NS,
        "DB": DB_DB,
    }
    auth = (DB_USER, DB_PASS)
    use_prefix = f"USE NS {DB_NS} DB {DB_DB}; "
    
    async with httpx.AsyncClient() as client:
        for name, config in servers.items():
            print(f"Processing '{name}'...")
            
            # Check existence
            check_sql = use_prefix + f"SELECT * FROM mcp_server WHERE name = '{name}';"
            resp = await client.post(DB_URL, content=check_sql, auth=auth, headers=headers)
            
            exists = False
            try:
                data = resp.json()
                if isinstance(data, list) and data[-1].get("status") == "OK" and data[-1].get("result"):
                    exists = True
            except Exception as e:
                print(f"  Error checking existence: {e}")
            
            if exists:
                print(f"  ✅ '{name}' already exists in DB. Skipping overwrite (preserving DB state).")
                # Optional: Force update if you want YAML to be authority, but typically DB is stateful override.
                # Since we want to FIX missing ones, skipping existing is safer for now.
                # However, ensure 'project-memory' is enabled if it exists but is disabled? 
                # No, it didn't exist in my check.
                continue
            
            # Prepare payload
            # Expand command/args if needed, but config.py handles normalization.
            # YAML format: 
            #   cmd: [executable, arg1, ...] 
            # DB format:
            #   command: executable
            #   args: [arg1, ...]
            
            cmd_list = config.get("cmd", [])
            command = cmd_list[0] if cmd_list else ""
            args = cmd_list[1:] if len(cmd_list) > 1 else []
            
            payload = {
                "name": name,
                "command": command,
                "args": args,
                "env": config.get("env", {}),
                "enabled": config.get("enabled", True),
                "type": config.get("type", "stdio")
            }
            
            if "disabled_reason" in config:
                payload["disabled_reason"] = config["disabled_reason"]

            # Insert
            insert_sql = use_prefix + f"CREATE mcp_server CONTENT {json.dumps(payload)};"
            resp = await client.post(DB_URL, content=insert_sql, auth=auth, headers=headers)
            
            if resp.status_code == 200:
                print(f"  🚀 Created '{name}' in DB.")
            else:
                print(f"  ❌ Failed to create '{name}': {resp.status_code} {resp.text}")

if __name__ == "__main__":
    asyncio.run(migrate_servers())
