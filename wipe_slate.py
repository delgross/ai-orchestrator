
import asyncio
import logging
import sys
import os

# Add path
sys.path.append(os.getcwd())

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wipe_slate")

async def main():
    print("Initializing State and Memory Server...")
    state = AgentState()
    memory = MemoryServer(state)
    
    # Manually initialize connection since we aren't using the full runner
    await memory.initialize()
    
    print("WARNING: Starting CLEAN SLATE Protocol...")
    print("1. Wiping ALL Chat History (episode)...")
    await memory._execute_query("DELETE episode;")
    
    print("2. Wiping ALL Learned Facts (fact)...")
    await memory._execute_query("DELETE fact;")
    
    print("3. Purging Ghost MCP Servers...")
    ghosts = ['exa', 'perplexity', 'tavily', 'firecrawl']
    for ghost in ghosts:
        # Check if exists first just to see
        # But DELETE WHERE name=... is safe enough
        q = f"DELETE mcp_server WHERE name = '{ghost}';"
        await memory._execute_query(q)
        print(f"   - Purged {ghost}")
        
    print("\nVerifying Purge...")
    res = await memory._execute_query("SELECT name FROM mcp_server")
    remaining = [r['name'] for r in res] if res else []
    print(f"Remaining MCP Servers: {remaining}")
    
    print("\nSlate Wiped Successfully.")

if __name__ == "__main__":
    asyncio.run(main())
