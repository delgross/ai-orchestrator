import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

# Removed bad imports


async def check_backlog():
    # We need to initialize the state mainly for config/client
    # Mocking minimal state if needed or relying on defaults
    
    # We'll use the HTTP interface of the running agent instead of internal calls 
    # to avoid complex setup if possible, OR just use the tool proxy if we can spin up registry.
    # Actually, simpler: Use `curl` to the /admin/mcp/execute endpoint if running? 
    # No, agent_runner is running. Let's use the internal proxy via a small script that
    # connects to the running service? No, that's hard.
    
    # Let's just use the HTTP API of the running agent!
    # Much cleaner than importing internals.
    import httpx
    
    async with httpx.AsyncClient() as client:
        # call get_memory_stats via system control? No, project-memory directly via mcp proxy endpoint
        # The agent exposes /mcp/execute ? No. 
        # But we can use the `mcp_proxy` tool via /chat or just Look at the DB directly?
        # Accessing DB directly is easiest if we have the creds.
        pass

    # Actually, the agent_runner is running.
    # Let's use the tool_mcp_proxy by importing it?
    # No, we can't easily attach to the running loop.
    
    # Plan B: use the /admin/mcp/debug/call endpoint
    import httpx
    
    auth_headers = {} # No auth for localhost/admin usually?
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://127.0.0.1:5460/admin/mcp/debug/call",
            json={
                "server": "project-memory",
                "tool": "get_memory_stats",
                "arguments": {}
            },
            timeout=10.0
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok"):
                stats = data.get("result", {})
                print(f"Total Episodes: {stats.get('episode_count')}")
                print(f"Unconsolidated: {stats.get('unconsolidated_count', 'Unknown')}")
            else:
                print(f"Error: {data.get('error')}")
        else:
            print(f"HTTP Error: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    asyncio.run(check_backlog())
