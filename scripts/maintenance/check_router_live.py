#!/usr/bin/env python3
"""Check what the RUNNING router process has loaded"""
import httpx
import asyncio

async def check_router_config():
    """Query router's /health endpoint which should show config"""
    try:
        async with httpx.AsyncClient() as client:
            # Health endpoint usually doesn't require auth
            resp = await client.get("http://127.0.0.1:5455/health")
            print("=== Router Health Response ===")
            print(resp.json())
            
            # Try getting models without auth
            resp2 = await client.get("http://127.0.0.1:5455/v1/models")
            print("\n=== Models Endpoint (no auth) ===")
            print(f"Status: {resp2.status_code}")
            print(resp2.text[:200])
            
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check_router_config())
