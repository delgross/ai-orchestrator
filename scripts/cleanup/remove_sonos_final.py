import asyncio
import os
import sys

sys.path.append(os.getcwd())
from agent_runner.memory_server import MemoryServer

async def main():
    try:
        print("Initializing MemoryServer...")
        mem = MemoryServer(state=None)
        await mem.initialize()
        
        target = "sonos-ts-mcp"
        print(f"Checking for server '{target}'...")
        res = await mem._execute_query(f"SELECT * FROM mcp_server WHERE name = '{target}'")
        
        if res:
            print(f"Found {len(res)} entry for '{target}'. Deleting...")
            del_res = await mem._execute_query(f"DELETE mcp_server WHERE name = '{target}'")
            print(f"Deletion Result: {del_res}")
            print("SUCCESS: Sonos server removed from Sovereign Memory.")
        else:
            print(f"Server '{target}' not found in database.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
