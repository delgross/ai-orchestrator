
import asyncio
import sys
import os
import httpx
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

SURREAL_URL = "http://localhost:8000/sql"
HEADERS = {
    "Accept": "application/json",
    "NS": "orchestrator",
    "DB": "memory",
    "Authorization": "Basic cm9vdDpyb290" # root:root
}

async def run_query(sql):
    async with httpx.AsyncClient() as client:
        try:
            # Explicitly use NS/DB in the query body too, just to be safe
            full_sql = f"USE NS orchestrator DB memory; {sql}"
            resp = await client.post(SURREAL_URL, content=full_sql, headers=HEADERS)
            print(f"SQL: {sql}")
            print(f"STATUS: {resp.status_code}")
            print(f"RESP: {resp.text}\n")
            return resp.json()
        except Exception as e:
            print(f"ERROR: {e}")

async def main():
    print("=== MIGRATING DATABASE SCHEMA TO 768 DIMENSIONS ===\n")
    
    # 1. Check current info
    await run_query("INFO FOR TABLE fact;")

    # 2. Drop the incorrect fields
    # We remove the field definition so SurrealDB stops enforcing 1024
    await run_query("REMOVE FIELD embedding ON TABLE fact;")
    await run_query("REMOVE FIELD embedding ON TABLE tool_definition;")

    # 3. Redefine with correct dimension (768)
    # This matches ollama:embeddinggemma:300m and nomic-embed-text
    await run_query("DEFINE FIELD embedding ON TABLE fact TYPE array<float, 768>;")
    await run_query("DEFINE FIELD embedding ON TABLE tool_definition TYPE array<float, 768>;")

    # 4. Verify
    print("=== MIGRATION COMPLETE. VERIFYING... ===")
    await run_query("INFO FOR TABLE fact;")

if __name__ == "__main__":
    asyncio.run(main())
