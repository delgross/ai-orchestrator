import asyncio
import os
import sys

sys.path.append(os.getcwd())
from agent_runner.memory_server import MemoryServer

async def main():
    mem = MemoryServer(state=None)
    await mem.initialize()
    
    servers = await mem._execute_query("SELECT * FROM mcp_server WHERE name = 'sonos-ts-mcp'")
    if servers:
        s = servers[0]
        print(f"Command: {s.get('command')}")
        print(f"Args: {s.get('args')}")
        print(f"Env: {s.get('env')}")

if __name__ == "__main__":
    asyncio.run(main())
