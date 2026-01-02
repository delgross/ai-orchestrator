
import asyncio
import sys
import httpx
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

SURREAL_URL = "http://localhost:8000/sql"
HEADERS = {
    "Accept": "application/json",
    "NS": "orchestrator",
    "DB": "memory",
    "Authorization": "Basic cm9vdDpyb290"
}

async def run_query(sql):
    async with httpx.AsyncClient() as client:
        try:
            full_sql = f"USE NS orchestrator DB memory; {sql}"
            resp = await client.post(SURREAL_URL, content=full_sql, headers=HEADERS)
            print(f"SQL: {sql}")
            print(f"RESP: {resp.text}\n")
        except Exception as e:
            print(f"ERROR: {e}")

async def main():
    print("=== DEBUGGING KB_ID STORAGE ===\n")
    # 1. Select raw facts
    await run_query("SELECT id, entity, kb_id, context FROM fact ORDER BY timestamp DESC LIMIT 5;")
    
    # 2. Check Table Info
    await run_query("INFO FOR TABLE fact;")

if __name__ == "__main__":
    asyncio.run(main())
