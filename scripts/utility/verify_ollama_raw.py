import httpx
import json
import asyncio
import sys

async def test_stream():
    url = "http://127.0.0.1:11434/api/chat"
    # Ollama native API
    payload = {
        "messages": [{"role": "user", "content": "What is the capital of the Sun?"}],
        "model": "mistral:latest",
        "stream": True # Ollama uses streaming by default, but explicit is good
    }
    
    print(f"Connecting to {url} (Raw Ollama)...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                print(f"Status Code: {response.status_code}")
                if response.status_code != 200:
                    print(f"Error Body: {await response.aread()}")
                    return

                print("--- Stream Start ---")
                count = 0
                async for line in response.aiter_lines():
                    if not line.strip(): continue
                    # Ollama sends JSON objects, one per line (NDJSON), NOT SSE "data: ..." by default on /api/chat?
                    # Wait, /api/chat returns NDJSON.
                    print(f"RAW: {line[:50]}...")
                    count += 1
                
                print(f"\nTotal Lines: {count}")
                            
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == "__main__":
    if "uvloop" in sys.modules:
        import uvloop
        uvloop.install()
    asyncio.run(test_stream())
