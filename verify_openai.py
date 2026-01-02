import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def check_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY is missing")
        return

    print(f"Checking OpenAI with Key: {api_key[:8]}...")
    
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers, timeout=10.0)
            if r.status_code == 200:
                print("✅ OpenAI Connectivity: OK")
                models = r.json()['data']
                print(f"Found {len(models)} models.")
            else:
                print(f"❌ OpenAI Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

asyncio.run(check_openai())
