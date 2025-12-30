import httpx
import json
import asyncio
import sys

async def test_stream():
    url = "http://127.0.0.1:5455/v1/chat/completions"
    # Use the underlying model directly
    payload = {
        "messages": [{"role": "user", "content": "What is the capital of the Sun?"}],
        "model": "ollama:mistral:latest", 
        "stream": True
    }
    headers = {"Authorization": "Bearer 9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic"}
    
    print(f"Connecting to {url} (Direct Model Access)...")
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                print(f"Status Code: {response.status_code}")
                if response.status_code != 200:
                    print(f"Error Body: {await response.aread()}")
                    return

                print("--- Stream Start ---")
                count = 0
                async for line in response.aiter_lines():
                    if not line.strip(): continue
                    # print(f"RAW: {line[:100]}...") # truncate for sanity
                    
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            print("\n--- Stream End [DONE] ---")
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    print(content, end="", flush=True)
                                    count += 1
                        except: pass
                
                print(f"\nTotal Content Chunks: {count}")
                            
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == "__main__":
    if "uvloop" in sys.modules:
        import uvloop
        uvloop.install()
    asyncio.run(test_stream())
