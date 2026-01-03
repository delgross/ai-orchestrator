
import asyncio
import httpx
import json

async def check_active_servers():
    url = "http://localhost:5460/admin/mcp/debug/call"
    
    payload = {
        "server": "system-control",
        "tool": "list_active_mcp_servers",
        "arguments": {}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("Calling list_active_mcp_servers...")
            resp = await client.post(url, json=payload, timeout=30.0)
            if resp.status_code == 200:
                print("Success:")
                print(json.dumps(resp.json(), indent=2))
            else:
                print(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"Exception: {repr(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_active_servers())
