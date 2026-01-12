import asyncio
import os
import sys

# Set path to include 'ai' so imports work
sys.path.append(os.getcwd())

from agent_runner.memory_server import MemoryServer

async def main():
    print("Initializing MemoryServer...")
    mem = MemoryServer(state=None)
    # Mocking ensure_connected logs
    await mem.initialize()
    
    print("Querying MCP Servers...")
    # Select name from mcp_server
    servers = await mem._execute_query("SELECT * FROM mcp_server")
    
    if not servers:
        print("No servers found.")
        return

    print(f"Found {len(servers)} servers.")
    for s in servers:
        name = s.get('name')
        print(f"- {name} (Type: {s.get('type')})")
        
        # Identify the duplicate "sonos" entry (NOT sonos-ts-mcp)
        # OR if both are present, remove one.
        # Check logic:
        # If we see "sonos" AND "sonos-ts-mcp", we delete "sonos".
        if name == 'sonos':
            print(f"  -> FOUND DUPLICATE 'sonos'! Deleting...")
            res = await mem._execute_query(f"DELETE mcp_server WHERE name = '{name}'")
            print(f"  Result: {res}")
        elif 'sonos' in name and name != 'sonos-ts-mcp':
             print(f"  -> Found suspicious server '{name}'. Deleting...")
             res = await mem._execute_query(f"DELETE mcp_server WHERE name = '{name}'")
             print(f"  Result: {res}")

if __name__ == "__main__":
    asyncio.run(main())
