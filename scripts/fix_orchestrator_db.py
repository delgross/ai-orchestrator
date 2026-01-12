
import yaml
import asyncio
import httpx
import json
import os

MCP_YAML_PATH = "/Users/bee/Sync/Antigravity/ai/config/mcp.yaml"
DB_URL = "http://127.0.0.1:8000/sql"
DB_NS = "orchestrator"  # CORRECT NAMESPACE
DB_DB = "memory"        # CORRECT DB
DB_USER = "root"
DB_PASS = "root"
TOKEN_VALUE = "antigravity_router_token_2025"

def load_yaml_config():
    with open(MCP_YAML_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return config.get("mcp_servers", {})

async def fix_orchestrator():
    print(f"Connecting to SurrealDB (CORRECT TARGET) at {DB_URL} ({DB_NS}/{DB_DB})...")
    
    headers = {
        "Accept": "application/json",
        "NS": DB_NS,
        "DB": DB_DB,
    }
    auth = (DB_USER, DB_PASS)
    use_prefix = f"USE NS {DB_NS} DB {DB_DB}; "
    
    async with httpx.AsyncClient() as client:
        # 1. SET ROUTER TOKEN
        print("Setting ROUTER_AUTH_TOKEN...")
        token_sql = use_prefix + f"""
        LET $exists = SELECT * FROM config_state WHERE key = 'ROUTER_AUTH_TOKEN';
        IF array::len($exists) == 0 THEN
            REMOVE $exists;
            CREATE config_state CONTENT {{ key: 'ROUTER_AUTH_TOKEN', value: '{TOKEN_VALUE}', source: 'fix_orchestrator' }};
        ELSE
            UPDATE config_state SET value = '{TOKEN_VALUE}' WHERE key = 'ROUTER_AUTH_TOKEN';
        END;
        """
        await client.post(DB_URL, content=token_sql, auth=auth, headers=headers)
        print("✅ ROUTER_AUTH_TOKEN fixed.")

        # 2. MIGRATE SERVERS
        servers = load_yaml_config()
        print(f"Migrating {len(servers)} servers...")
        
        for name, config in servers.items():
            # Check existence
            check_sql = use_prefix + f"SELECT * FROM mcp_server WHERE name = '{name}';"
            resp = await client.post(DB_URL, content=check_sql, auth=auth, headers=headers)
            
            exists = False
            try:
                data = resp.json()
                if isinstance(data, list) and data[-1].get("status") == "OK" and data[-1].get("result"):
                     exists = True
            except:
                pass
            
            if exists:
                print(f"  Existing '{name}': Updating enabled=true to fix potential disabled state.")
                update_sql = use_prefix + f"UPDATE mcp_server SET enabled = true, disabled_reason = NONE WHERE name = '{name}';"
                await client.post(DB_URL, content=update_sql, auth=auth, headers=headers)
                continue
                
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
             # Handle optional disabled_reason from YAML
            if "disabled_reason" in config:
                payload["disabled_reason"] = config["disabled_reason"]

            # Insert
            insert_sql = use_prefix + f"CREATE mcp_server CONTENT {json.dumps(payload)};"
            resp = await client.post(DB_URL, content=insert_sql, auth=auth, headers=headers)
            
            if resp.status_code == 200:
                print(f"  🚀 Created '{name}'.")
            else:
                print(f"  ❌ Failed to create '{name}'.")

if __name__ == "__main__":
    asyncio.run(fix_orchestrator())
