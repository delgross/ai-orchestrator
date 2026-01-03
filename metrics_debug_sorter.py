
import asyncio
import logging
import os
import sys

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Mock Config
config = {
    "surreal": {"url": "http://localhost:8000"},
    "agent_runner": {"fallback": {"model": "ollama:mistral:latest"}} # Use Mistral for speed
}

# Add path
sys.path.append(os.getcwd())

from agent_runner.services.log_sorter import LogSorterService

async def main():
    print("Initializing Debug Sorter...")
    sorter = LogSorterService(config)
    print(f"NS: {sorter.surreal_ns}, DB: {sorter.surreal_db}")
    
    import httpx
    async with httpx.AsyncClient() as client:
        # Check Count
        query_count = f"USE NS {sorter.surreal_ns}; USE DB {sorter.surreal_db}; SELECT count() FROM diagnostic_log WHERE handled IS NONE GROUP ALL;"
        print(f"Query Count: {query_count}")
        resp = await client.post(
            f"{sorter.surreal_url}/sql",
            content=query_count, 
            auth=sorter.surreal_auth,
            headers={"Accept": "application/json", "Content-Type": "text/plain"}
        )
        print(f"Count Data: {resp.json()}")

        # Check All Fields
        query = f"USE NS {sorter.surreal_ns}; USE DB {sorter.surreal_db}; SELECT * FROM diagnostic_log WHERE handled IS NONE LIMIT 5;"
        print(f"Query All: {query}")
        resp = await client.post(
            f"{sorter.surreal_url}/sql",
            content=query, 
            auth=sorter.surreal_auth,
            headers={"Accept": "application/json", "Content-Type": "text/plain"}
        )
        print(f"Raw Data: {resp.json()}")

if __name__ == "__main__":
    asyncio.run(main())
