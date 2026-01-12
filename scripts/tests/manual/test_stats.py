import asyncio
import httpx
import os

async def check():
    url = "http://127.0.0.1:8000/sql"
    headers = {"Accept": "application/json", "NS": "orchestrator", "DB": "memory"}
    auth = ("root", "root")
    async with httpx.AsyncClient() as client:
        # Check Fact Count
        resp = await client.post(url, content="SELECT count() FROM fact GROUP ALL", auth=auth, headers=headers)
        print(f"Fact Count: {resp.text}")
        
        # Check specific OMEGA record
        resp2 = await client.post(url, content="SELECT * FROM fact WHERE content CONTAINS 'OMEGA' OR target CONTAINS 'OMEGA'", auth=auth, headers=headers)
        print(f"Omega Record: {resp2.text}")

if __name__ == "__main__":
    asyncio.run(check())
