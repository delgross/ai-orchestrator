
import asyncio
import httpx
import json

DB_URL = "http://127.0.0.1:8000/sql"
DB_NS = "antigravity"
DB_DB = "antigravity"
DB_USER = "root"
DB_PASS = "root"
TOKEN_VALUE = "antigravity_router_token_2025"

async def set_token():
    print(f"Connecting to SurrealDB at {DB_URL}...")
    headers = {
        "Accept": "application/json",
        "NS": DB_NS,
        "DB": DB_DB,
    }
    auth = (DB_USER, DB_PASS)
    
    async with httpx.AsyncClient() as client:
        use_prefix = f"USE NS {DB_NS} DB {DB_DB}; "
        
        # Upsert mechanism
        # Check if exists
        check_sql = use_prefix + "SELECT * FROM config_state WHERE key = 'ROUTER_AUTH_TOKEN';"
        resp = await client.post(DB_URL, content=check_sql, auth=auth, headers=headers)
        
        exists = False
        try:
             data = resp.json()
             if isinstance(data, list) and data[-1].get("result"):
                 exists = True
        except:
            pass
            
        if exists:
            print("Updating existing token...")
            update_sql = use_prefix + f"UPDATE config_state SET value = '{TOKEN_VALUE}' WHERE key = 'ROUTER_AUTH_TOKEN';"
            await client.post(DB_URL, content=update_sql, auth=auth, headers=headers)
        else:
            print("Creating new token...")
            payload = {
                "key": "ROUTER_AUTH_TOKEN",
                "value": TOKEN_VALUE,
                "source": "manual_fix"
            }
            create_sql = use_prefix + f"CREATE config_state CONTENT {json.dumps(payload)};"
            await client.post(DB_URL, content=create_sql, auth=auth, headers=headers)
            
        print("✅ ROUTER_AUTH_TOKEN set successfully.")

if __name__ == "__main__":
    asyncio.run(set_token())
