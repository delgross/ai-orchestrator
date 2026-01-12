
import asyncio
import httpx
import json

DB_URL = "http://127.0.0.1:8000/sql"
DB_USER = "root"
DB_PASS = "root"
DB_NS = "antigravity"
DB_DB = "antigravity"

async def check_memory_status():
    print(f"Connecting to SurrealDB at {DB_URL}...")
    
    headers = {
        "Accept": "application/json",
        "NS": DB_NS,
        "DB": DB_DB,
    }
    auth = (DB_USER, DB_PASS)
    
    async with httpx.AsyncClient() as client:
        use_prefix = f"USE NS {DB_NS} DB {DB_DB}; "
        check_sql = use_prefix + "SELECT * FROM mcp_server WHERE name = 'project-memory';"
        print(f"Executing: {check_sql}")
        
        try:
            resp = await client.post(DB_URL, content=check_sql, auth=auth, headers=headers)
            if resp.status_code != 200:
                print(f"Failed to query DB: {resp.status_code} {resp.text}")
                return

            data = resp.json()
            # print(f"Raw: {json.dumps(data, indent=2)}")
            
            # Surreal returns list of results. Expected: [USE result, SELECT result]
            if isinstance(data, list) and len(data) >= 2:
                select_res = data[-1]
                if select_res.get("status") == "OK":
                     results = select_res.get("result", [])
                     if not results:
                         print("❌ 'project-memory' NOT FOUND in database.")
                     else:
                         server = results[0]
                         print(f"✅ Found 'project-memory':")
                         print(f"   Enabled: {server.get('enabled')}")
                         print(f"   Disabled Reason: {server.get('disabled_reason')}")
                         print(f"   Command: {server.get('command')}")
                         print(f"   Env: {server.get('env')}")
                else:
                    print(f"Query Error: {select_res}")
            else:
                print(f"Unexpected response format: {data}")

        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(check_memory_status())
