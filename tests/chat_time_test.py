import asyncio
import json
import time
import httpx

ROUTER_URL = "http://127.0.0.1:5455/v1/chat/completions"

async def measure_time_check():
    payload = {
        "model": "agent:mcp",
        "messages": [{"role": "user", "content": "What time is it?"}],
        "stream": True
    }
    
    print(f"🚀 Sending 'Time Check' request to {ROUTER_URL}...")
    start_time = time.time()
    ttft = 0
    first_token_time = None
    
    headers = {
        "Authorization": "Bearer antigravity_router_token_2025"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream("POST", ROUTER_URL, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    print(f"❌ Error: {response.status_code} - {await response.aread()}")
                    return

                print("⏳ Waiting for stream...")
                async for chunk in response.aiter_lines():
                    if not chunk.strip():
                        continue
                    if chunk == "data: [DONE]":
                        break
                    
                    if not first_token_time:
                        first_token_time = time.time()
                        ttft = first_token_time - start_time
                        print(f"⏱️ TTFT (First Response): {ttft:.4f}s")
                    
                    # Try to parse content to see if it's a "Thought" or "Tool Call"
                    try:
                        if chunk.startswith("data: "):
                            data = json.loads(chunk[6:])
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                # Print first few chars to see if it's thinking
                                pass
                    except:
                        pass
        except Exception as e:
            print(f"❌ Exception: {e}")
            return

    total_time = time.time() - start_time
    print(f"🏁 Total Interaction Time: {total_time:.4f}s")
    
    if ttft > 2.0:
        print("⚠️ FAIL: TTFT > 2s (Latency Issue)")
    else:
        print("✅ PASS: TTFT < 2s")

if __name__ == "__main__":
    asyncio.run(measure_time_check())
