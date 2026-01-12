
import asyncio
import httpx
import json
import os

DB_URL = "http://127.0.0.1:8000/sql"
DB_NS = "antigravity"
DB_DB = "antigravity"
DB_USER = "root"
DB_PASS = "root"

async def check_token():
    print(f"Connecting to SurrealDB at {DB_URL}...")
    headers = {
        "Accept": "application/json",
        "NS": DB_NS,
        "DB": DB_DB,
    }
    auth = (DB_USER, DB_PASS)
    
    async with httpx.AsyncClient() as client:
        use_prefix = f"USE NS {DB_NS} DB {DB_DB}; "
        sql = use_prefix + "SELECT * FROM config_state WHERE key = 'ROUTER_AUTH_TOKEN';"
        resp = await client.post(DB_URL, content=sql, auth=auth, headers=headers)
        print(f"DB Response: {resp.text}")
        
    print(f"OS Env check: ROUTER_AUTH_TOKEN present? {'ROUTER_AUTH_TOKEN' in os.environ}")

if __name__ == "__main__":
    asyncio.run(check_token())
