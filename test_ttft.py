
import asyncio
import time
import httpx
import json

async def test_ttft():
    url = "http://127.0.0.1:5460/v1/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": "Write a long poem about rust."}], # Request long output to separate TTFT from Total
        "stream": True, # CRITICAL: Test streaming
        "model": "agent:mcp"
    }
    
    print(f"🚀 PROBING TTFT at {url}...")
    t0 = time.time()
    first_token_time = None
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                print(f"Connected in {time.time() - t0:.2f}s (Headers Received)")
                
                async for chunk in response.aiter_lines():
                    if not chunk.strip(): continue
                    if chunk.startswith("data: [DONE]"): break
                    if chunk.startswith("data: "):
                        if first_token_time is None:
                            first_token_time = time.time()
                            ttft = first_token_time - t0
                            print(f"⏱️ **TTFT (Time To First Token): {ttft:.4f}s**")
                        
                        # data = json.loads(chunk[6:])
                        # content = data['choices'][0]['delta'].get('content', '')
                        # print(content, end="", flush=True)
                        
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    for i in range(1, 6):
        print(f"\n🔁 RUN {i}/5")
        asyncio.run(test_ttft())
        time.sleep(1)
