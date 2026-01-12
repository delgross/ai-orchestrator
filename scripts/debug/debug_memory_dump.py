
import asyncio
import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent_runner.registry import ServiceRegistry
from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

logging.basicConfig(level=logging.INFO)

async def dump():
    print("--- Memory Dump ---")
    state = AgentState()
    # Ensure config allows connection
    state.config = {"ai": {"embedding_model": "mxbai-embed-large:latest"}}
    ServiceRegistry.register_state(state)
    
    memory = MemoryServer(state)
    await memory.initialize()
    
    print("Membank Config:", await memory.list_memory_banks())
    
    # Count check
    count_res = await memory._execute_query("SELECT count() FROM fact GROUP ALL")
    print(f"Total Fact Count: {count_res}")

    # Raw query with embedding check
    res = await memory._execute_query("SELECT id, entity, relation, target, confidence, created_at, array::len(embedding) as emb_len FROM fact ORDER BY created_at DESC LIMIT 10")
    if res:
        print(f"Found {len(res)} facts:")
        for r in res:
            print(r)
    else:
        print("No facts found (or query failed).")

if __name__ == "__main__":
    asyncio.run(dump())
