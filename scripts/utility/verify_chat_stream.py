import httpx
import json
import asyncio
import sys

async def test_stream():
    url = "http://127.0.0.1:5455/v1/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": "What is the capital of the Sun?"}],
        "model": "agent:mcp",
        "stream": True
    }
    headers = {"Authorization": "Bearer 9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic"}
    
    print(f"Connecting to {url}...")
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                print(f"Status Code: {response.status_code}")
                if response.status_code != 200:
                    print(f"Error Body: {await response.aread()}")
                    return

                print("--- Stream Start ---")
                async for line in response.aiter_lines():
                    if not line.strip(): continue
                    print(f"RAW: {line}")
                    
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            print("--- Stream End [DONE] ---")
                            break
                        try:
                            # Try parsing to see what we get
                            chunk = json.loads(data_str)
                            # Inspect structure
                            content = "N/A"
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta: content = f"Content('{delta['content']}')"
                                elif "type" in delta: content = f"CustomEvent({delta['type']})"
                            
                            print(f"PARSED: ID={chunk.get('id')} Model={chunk.get('model')} Payload={content}")
                        except Exception as e:
                            print(f"PARSE ERROR: {e}")
                            
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == "__main__":
    if "uvloop" in sys.modules:
        import uvloop
        uvloop.install()
    asyncio.run(test_stream())
