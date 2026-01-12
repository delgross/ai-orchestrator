
import asyncio
import httpx
import sys
import json
import time

BASE_URL = "http://127.0.0.1:5460"

async def execute_tool(tool_name: str, args: dict):
    # Try probable paths due to prefix confusion
    paths = ["/admin/admin/tools/execute", "/admin/tools/execute"]
    
    async with httpx.AsyncClient() as client:
        for p in paths:
            try:
                url = f"{BASE_URL}{p}"
                resp = await client.post(url, json={
                    "tool_name": tool_name,
                    "arguments": args
                }, timeout=10.0)
                if resp.status_code != 404:
                    data = resp.json()
                    print(f"[DEBUG] {p} Response: {data}")
                    if resp.status_code == 200:
                         return data.get("result", data)
                    else:
                         print(f"Error {resp.status_code} on {p}: {resp.text}")
                         return {}
            except Exception:
                pass
    print("Failed to find tool execution endpoint.")
    return {}

async def check_status_direct():
    # Try /admin/system-status and /admin/admin/system-status
    paths = ["/admin/admin/system-status", "/admin/system-status"]
    async with httpx.AsyncClient() as client:
        for p in paths:
            try:
                resp = await client.get(f"{BASE_URL}{p}", timeout=5.0)
                if resp.status_code == 200:
                    return resp.json()
            except:
                pass
    return {}

async def main():
    print("Waiting for reload...")
    await asyncio.sleep(3)
    
    # 1. Check Initial Mode
    status = await check_status_direct()
    mode = status.get("active_mode", "UNKNOWN").upper()
    print(f"Initial Mode: {mode}")

    if mode == "UNKNOWN":
        print("❌ Could not read active_mode from status.")
        return

    # 2. Switch to CODING
    print("Switching to CODING...")
    res = await execute_tool("set_mode", {"mode": "coding"})
    print(f"Tool Result: {res}")
    
    await asyncio.sleep(1)
    
    # 3. Verify
    status = await check_status_direct()
    new_mode = status.get("active_mode", "UNKNOWN").upper()
    print(f"New Mode: {new_mode}")
    
    if new_mode == "CODING":
        print("✅ SUCCESS: Mode switched to CODING")
    else:
        print("❌ FAILURE: Mode did not switch.")
        
    # 4. Reset
    await execute_tool("set_mode", {"mode": "chat"})
    print("Reset to CHAT.")

if __name__ == "__main__":
    asyncio.run(main())
