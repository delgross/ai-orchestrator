import asyncio
import os
import sys
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

async def verify_grok():
    print("--- Verifying Grok (xAI) ---")
    
    # Load env
    root = Path(__file__).parent.parent
    load_dotenv(root / ".env")
    load_dotenv(root / "providers.env")
    
    key = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
    if not key:
        print("❌ FAILED: XAI_API_KEY (or GROK_API_KEY) not found in .env")
        return

    print("🔑 Key found.")
    
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    # Try the most stable alias first
    model = "grok-3" 
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": "You are a test script."}, {"role": "user", "content": "Say 'Grok Lives!'"}],
        "stream": False
    }
    
    print(f"📡 Connecting to {url} with model '{model}'...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            
            if resp.status_code == 200:
                print(f"✅ SUCCESS: {resp.json()['choices'][0]['message']['content']}")
            else:
                print(f"❌ FAILED ({resp.status_code}): {resp.text}")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(verify_grok())
