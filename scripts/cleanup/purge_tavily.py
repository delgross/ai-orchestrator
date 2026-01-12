
import asyncio
import sys
import os

# Add path
sys.path.append(os.getcwd())

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

async def main():
    state = AgentState()
    memory = MemoryServer(state)
    await memory.initialize()
    
    print("Purging tavily-search...")
    await memory._execute_query("DELETE mcp_server WHERE name = 'tavily-search';")
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
