
import asyncio
import time
import httpx
import json

async def test_latency():
    endpoints = [
        "http://127.0.0.1:5460/api/chat/completions",
        "http://127.0.0.1:5460/v1/chat/completions",
        "http://127.0.0.1:5460/chat/completions"
    ]
    
    payload = {
        "messages": [{"role": "user", "content": "What time is it?"}],
        "stream": False,
        "model": "agent:mcp"
    }
    
    for url in endpoints:
        print(f"🚀 PROBING {url}...")
        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, json=payload)
                dur = time.time() - t0
                
                print(f"⏱️ Response Time: {dur:.2f}s")
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"✅ SUCCESS! Response: {resp.text[:200]}...")
                    break
                else:
                     print(f"❌ Error: {resp.text}")
        except Exception as e:
            print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_latency())
