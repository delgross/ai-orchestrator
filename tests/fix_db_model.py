
import asyncio
import httpx
import json

DB_URL = "http://127.0.0.1:8000/sql"
DB_NS = "orchestrator"
DB_DB = "memory"
DB_USER = "root"
DB_PASS = "root"
CORRECT_MODEL = "ollama:llama3.1:latest"

async def fix_model():
    headers = {
        "Accept": "application/json",
        "NS": DB_NS,
        "DB": DB_DB,
    }
    auth = (DB_USER, DB_PASS)
    sql = f"USE NS {DB_NS} DB {DB_DB}; UPDATE config_state SET value = '{CORRECT_MODEL}' WHERE key = 'AGENT_MODEL'; UPDATE config_state SET value = '{CORRECT_MODEL}' WHERE key = 'TASK_MODEL';"
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(DB_URL, content=sql, auth=auth, headers=headers)
        print(f"Updated DB Response: {resp.text}")

if __name__ == "__main__":
    asyncio.run(fix_model())
