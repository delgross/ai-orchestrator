import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.memory_server import MemoryServer
from agent_runner.state import AgentState

async def migrate():
    print("--- Migrating Schema ---")
    state = AgentState()
    # state.agent_fs_root... (optional for this op)
    
    server = MemoryServer(state)
    await server.ensure_connected()
    
    print("Dropping old index...")
    try:
        await server._execute_query("REMOVE INDEX idx_episode_embedding ON episode")
        print("Index dropped.")
    except Exception as e:
        print(f"Drop failed (maybe didn't exist): {e}")
        
    print("Re-applying schema...")
    await server.ensure_schema()
    print("Schema applied.")

if __name__ == "__main__":
    asyncio.run(migrate())
