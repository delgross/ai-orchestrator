
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_runner.db_utils import run_query
from agent_runner.state import AgentState

async def disable_mcp():
    print("🔌 disabling filesystem MCP in Sovereign Memory...")
    
    # Initialize minimal state for DB connection
    state = AgentState()
    # Mock config for DB connection if needed, but AgentState loads env
    
    # We need to manually initialize memory server or just use the raw query if utils allows
    # db_utils.run_query uses state.memory.client
    
    # Let's try to initialize just enough
    from agent_runner.memory_server import MemoryServer
    state.memory = MemoryServer(state)
    await state.memory.initialize()
    
    # Update Query
    query = "UPDATE mcp_server SET enabled = false, disabled_reason = 'user_request_redundant' WHERE name = 'filesystem';"
    result = await state.memory._execute_query(query)
    
    print(f"✅ Result: {result}")
    
    # Verify
    verify = await state.memory._execute_query("SELECT name, enabled FROM mcp_server WHERE name = 'filesystem';")
    print(f"🔍 Verification: {verify}")

if __name__ == "__main__":
    asyncio.run(disable_mcp())
