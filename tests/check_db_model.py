
import asyncio
import httpx
import json

DB_URL = "http://127.0.0.1:8000/sql"
DB_NS = "orchestrator"
DB_DB = "memory"
DB_USER = "root"
DB_PASS = "root"

async def check_model():
    headers = {
        "Accept": "application/json",
        "NS": DB_NS,
        "DB": DB_DB,
    }
    auth = (DB_USER, DB_PASS)
    sql = f"USE NS {DB_NS} DB {DB_DB}; SELECT * FROM config_state WHERE key = 'AGENT_MODEL';"
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(DB_URL, content=sql, auth=auth, headers=headers)
        print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(check_model())
