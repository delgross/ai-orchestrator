import asyncio
import os
import sys

# Ensure correct path
sys.path.append(os.getcwd())

from agent_runner.executor import ToolExecutor
from agent_runner.state import AgentState

async def main():
    print("Initializing Agent State...")
    state = AgentState()
    # Mock minimal state components for discovery
    state.agent_fs_root = os.getcwd() # Needed for registry path
    # We need to load mcp_servers from DB really, but ToolExecutor doesn't load them.
    # The Agent Runner loads them into state.mcp_servers.
    
    # So we must mimic the loader:
    from agent_runner.memory_server import MemoryServer
    mem = MemoryServer(state)
    await mem.initialize()
    state.memory = mem
    
    from agent_runner.config import load_mcp_servers
    await load_mcp_servers(state)
    
    print(f"Loaded Servers: {list(state.mcp_servers.keys())}")
    
    print("Discovering Tools...")
    executor = ToolExecutor(state)
    await executor.discover_mcp_tools()
    
    mcp_tools = executor.mcp_tool_cache
    
    # Validation logic
    sonos_tools = mcp_tools.get("sonos-ts-mcp", [])
    control_sonos = any(t['function']['name'] == 'control_sonos' for t in executor.tool_definitions) # Native won't have it unless added?
    
    print(f"Sonos Tools Count: {len(sonos_tools)}")
    
    if "sonos-ts-mcp" in state.mcp_servers:
        print("FAILURE: sonos-ts-mcp still present in configuration!")
    else:
        print("SUCCESS: sonos-ts-mcp removed from configuration.")

    if len(sonos_tools) > 0:
         print("FAILURE: Sonos tools still discovered!")
    else:
         print("SUCCESS: No Sonos tools discovered.")

if __name__ == "__main__":
    asyncio.run(main())
