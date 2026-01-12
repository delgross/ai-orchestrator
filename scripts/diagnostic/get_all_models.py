
import asyncio
import httpx
import os
import json

# Configuration matching memory_server.py
SURREAL_URL = "http://127.0.0.1:8000/sql"
SURREAL_USER = "root"
SURREAL_PASS = "root"
SURREAL_NS = "agent" 
SURREAL_DB = "memory"

async def get_all_models():
    auth = (SURREAL_USER, SURREAL_PASS)
    headers = {
        "Accept": "application/json",
        "NS": SURREAL_NS,
        "DB": SURREAL_DB,
    }
    
    # Prepend explicit USE statement
    query = f"USE NS {SURREAL_NS} DB {SURREAL_DB}; SELECT * FROM config_state;"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SURREAL_URL, 
                content=query, 
                auth=auth, 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("--- RAW DB RESPONSE ---")
                print(json.dumps(data, indent=2))
                print("-----------------------")
            else:
                print(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_all_models())
