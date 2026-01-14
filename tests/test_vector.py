
import asyncio
import os
import httpx
import json

SURREAL_URL = "http://127.0.0.1:8000/sql"
HEADERS = {
    "Accept": "application/json",
    "NS": "orchestrator",
    "DB": "memory",
    "Authorization": "Basic cm9vdDpyb290" # root:root
}

async def run_query(sql, vars=None):
    if vars:
        # Surreal HTTP expects vars as extra fields? No, it expects SQL vars?
        # Actually it's easier to verify function existence with simple query.
        pass
    
    async with httpx.AsyncClient() as client:
        # Try to define a vector
        # CREATE test:1 SET v = [0.1, 0.2, 0.3];
        print(f"Executing: {sql}")
        resp = await client.post(SURREAL_URL, headers=HEADERS, data=sql)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

async def main():
    # Test 1: Check version (indirectly) or just availability of functions
    await run_query("RETURN vector::similarity::euclidean([1,2], [1,2]);")
    # Test 2: distance
    await run_query("RETURN vector::distance::euclidean([1,2], [1,2]);")
    # Test 3: math::sqrt?
    await run_query("RETURN math::sqrt(10);")
    # Test 4: cosine similarity?
    await run_query("RETURN vector::similarity::cosine([1,0], [0,1]);")


if __name__ == "__main__":
    asyncio.run(main())
