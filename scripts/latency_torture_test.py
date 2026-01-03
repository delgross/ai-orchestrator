import asyncio
import time
import json
import httpx
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor

TARGET_URL = "http://127.0.0.1:5455/v1/chat/completions"
PAYLOAD = {
    "model": "agent", 
    "messages": [{"role": "user", "content": "Ping. Latency Check."}],
    "stream": True  
}
HEADERS = {
    "Authorization": "Bearer 9sYBjBLjAHKG8g8ZzzsUeBOvtzgQFHmX7oIeygdpzic"
}

# Config
CONCURRENCY_LEVELS = [1]
TIMEOUT = 60.0

async def single_request(session, req_id):
    start = time.perf_counter()
    ttft = None
    end = None
    success = False
    error = None

    try:
        # We use a POST request with streaming enabled
        async with session.stream("POST", TARGET_URL, json=PAYLOAD, headers=HEADERS, timeout=TIMEOUT) as response:
            if response.status_code != 200:
                error = f"HTTP {response.status_code}"
                return {"success": False, "ttft": 0, "total": 0, "error": error}
            
            # Read chunks to find first token
            async for chunk in response.aiter_bytes():
                if ttft is None:
                    ttft = time.perf_counter() - start
                # We don't need to parse the whole stream for torture, just consume it
                pass
            
            end = time.perf_counter() - start
            success = True
            if ttft is None: # Empty response?
                ttft = end

    except Exception as e:
        error = str(e)
        return {"success": False, "ttft": 0, "total": 0, "error": error}

    return {
        "success": True, 
        "ttft": ttft * 1000, # ms
        "total": end * 1000, # ms
        "error": None
    }

async def run_batch(level):
    print(f"\n🔥 Running Batch: {level} concurrent requests...")
    async with httpx.AsyncClient(limits=httpx.Limits(max_keepalive_connections=level, max_connections=level)) as session:
        tasks = [single_request(session, i) for i in range(level)]
        results = await asyncio.gather(*tasks)
    
    # Analyze
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]
    
    if not successes:
        print(f"❌ Batch {level} FAILED completely. Errors: {set(r['error'] for r in failures)}")
        return

    ttfts = [r["ttft"] for r in successes]
    totals = [r["total"] for r in successes]

    print(f"✅ Success Rate: {len(successes)}/{level} ({len(successes)/level*100:.1f}%)")
    print(f"   TTFT (ms): Avg={statistics.mean(ttfts):.1f}, Min={min(ttfts):.1f}, Max={max(ttfts):.1f}, P95={statistics.quantiles(ttfts, n=20)[18]:.1f}")
    print(f"   Total(ms): Avg={statistics.mean(totals):.1f}, Min={min(totals):.1f}, Max={max(totals):.1f}")
    if failures:
        print(f"   Errors: {len(failures)} (Sample: {failures[0]['error']})")

async def main():
    print(f"🚀 Starting LATENCY TORTURE TEST on {TARGET_URL}")
    
    for level in CONCURRENCY_LEVELS:
        await run_batch(level)
        await asyncio.sleep(2) # Cool down

if __name__ == "__main__":
    asyncio.run(main())
