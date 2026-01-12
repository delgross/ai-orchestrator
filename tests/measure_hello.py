
import asyncio
import time
import httpx
import json

async def measure():
    url = "http://localhost:5455/v1/chat/completions"
    
    # Payload: Simple "Hello" to test Chat Latency without Tool Execution
    payload = {
        "model": "agent:mcp", 
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True
    }
    
    print(f"🚀 Sending 'Hello' to {url}...")
    start_time = time.time()
    
    headers = {
        "Authorization": "Bearer antigravity_router_token_2025"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    print(f"❌ Error: Status {response.status_code}")
                    content = await response.aread()
                    print(content.decode())
                    return

                print("✅ Connected. Receiving stream...")
                first_token = True
                token_count = 0
                
                async for chunk in response.aiter_lines():
                    if not chunk.strip(): continue
                    if chunk.startswith("data: "):
                        data_str = chunk[6:]
                        if data_str == "[DONE]": break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                token_count += 1
                                if first_token:
                                    t_first = time.time() - start_time
                                    print(f"⏱️ Time to First Token: {t_first*1000:.2f}ms")
                                    first_token = False
                        except: pass
                
                total_time = time.time() - start_time
                print(f"⏱️ Total Time to Complete: {total_time*1000:.2f}ms")
                print(f"📊 Total Tokens: {token_count}")
                tps = token_count / total_time
                print(f"⚡ Tokens Per Second: {tps:.2f}")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(measure())
