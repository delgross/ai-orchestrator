
import asyncio
import sys
import httpx
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

URL = "http://localhost:5460/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test-token" # If auth enabled
}

async def main():
    print("=== CHECKING AGENT REHYDRATION ===\n")
    
    payload = {
        "model": "ollama:llama3.3:70b-instruct-q8_0",
        "messages": [
            {"role": "user", "content": "What is your internal architecture? List 3 key components."}
        ],
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(URL, json=payload, headers=HEADERS)
            if resp.status_code != 200:
                print(f"Error: {resp.text}")
                return

            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            print(f"RESPONSE:\n{content}\n")
            
            # Check for keywords from our memory bank
            keywords = ["router", "agent_runner", "config.yaml", "surrealdb"]
            found = [k for k in keywords if k.lower() in content.lower()]
            
            if len(found) >= 2:
                print(f"\nPASS: Found internal keywords: {found}")
            else:
                print(f"\nFAIL: Missing internal keywords. Found: {found}")

    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
