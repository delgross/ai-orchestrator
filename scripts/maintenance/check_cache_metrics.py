#!/usr/bin/env python3
"""Check cache metrics to verify Phase 3 optimizations are working"""
import asyncio
import httpx

async def check_cache_status():
    """Query agent-runner for cache metrics"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check if executor has cache stats endpoint
            response = await client.get("http://127.0.0.1:5460/health")
            print("=== Agent Runner Health ===")
            print(response.json())
            
    except Exception as e:
        print(f"Error checking cache: {e}")

async def test_cache_behavior():
    """Make repeated identical requests to test MCP cache"""
    url = "http://127.0.0.1:5455/v1/chat/completions"
    headers = {"Authorization": "Bearer antigravity_router_token_2025"}
    payload = {
        "model": "agent",
        "messages": [{"role": "user", "content": "List files in the current directory"}],
        "stream": False
    }
    
    print("\n=== Testing MCP Response Cache ===")
    print("Making 3 identical filesystem requests...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i in range(3):
            import time
            start = time.perf_counter()
            resp = await client.post(url, json=payload, headers=headers)
            duration = (time.perf_counter() - start) * 1000
            print(f"Request {i+1}: {duration:.1f}ms (status: {resp.status_code})")
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(check_cache_status())
    # Uncomment to test cache behavior
    # asyncio.run(test_cache_behavior())
