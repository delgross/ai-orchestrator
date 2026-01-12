
import asyncio
import httpx
import json

# DB Configuration - mimicking MemoryServer
DB_URL = "http://127.0.0.1:8000/sql"
DB_USER = "root"
DB_PASS = "root"
DB_NS = "antigravity"
DB_DB = "antigravity"

async def seed_system_control():
    print(f"Connecting to SurrealDB at {DB_URL}...")
    
    headers = {
        "Accept": "application/json",
        "NS": DB_NS,
        "DB": DB_DB,
    }
    auth = (DB_USER, DB_PASS)
    
    async with httpx.AsyncClient() as client:
        # Check if exists
        use_prefix = f"USE NS {DB_NS} DB {DB_DB}; "
        check_sql = use_prefix + "SELECT * FROM mcp_server WHERE name = 'system-control';"
        print(f"Executing: {check_sql}")
        resp = await client.post(DB_URL, content=check_sql, auth=auth, headers=headers)
        
        if resp.status_code != 200:
            print(f"Failed to query DB: {resp.status_code} {resp.text}")
            return

        data = resp.json()
        print(f"Query Result: {json.dumps(data, indent=2)}")
        
        # Check if we have results
        exists = False
        try:
             # Surreal returns list of results for each statement
             # We sent USE...; SELECT...; so we expect 2 results.
             # Last one is the SELECT
             last_res = data[-1]
             if last_res.get("status") == "OK" and last_res.get("result"):
                 exists = True
        except Exception:
            pass
        
        if exists:
            print("System Control server already exists in DB. Ensuring enabled.")
            update_sql = use_prefix + "UPDATE mcp_server SET enabled = true WHERE name = 'system-control';"
            await client.post(DB_URL, content=update_sql, auth=auth, headers=headers)
            print("Updated enabled status.")
        else:
            print("Seeding 'system-control' server...")
            cmd = "/Users/bee/Sync/Antigravity/ai/.venv/bin/python"
            script = "/Users/bee/Sync/Antigravity/ai/agent_runner/system_control_server.py"
            
            payload = {
                "name": "system-control",
                "command": cmd,
                "args": [script],
                "env": {},
                "enabled": True,
                "type": "stdio"
            }
            
            # Using CONTENT keyword for easier JSON insertion
            insert_sql = use_prefix + f"CREATE mcp_server CONTENT {json.dumps(payload)};"
            print(f"Executing: {insert_sql}")
            
            resp = await client.post(DB_URL, content=insert_sql, auth=auth, headers=headers)
            print(f"Insert Response: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    asyncio.run(seed_system_control())
