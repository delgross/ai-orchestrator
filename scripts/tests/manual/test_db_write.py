import asyncio
import sys
# Add project root to path
sys.path.append("/Users/bee/Sync/Antigravity/ai")

from agent_runner.memory_server import MemoryServer
from agent_runner.state import AgentState

async def test_write():
    print("Initializing MemoryServer...")
    ms = MemoryServer()
    await ms.initialize()
    
    print("Attempting to store fact...")
    res = await ms.store_fact("TestEntity", "is_testing", "Writability", context="Manual Test", confidence=1.0)
    print(f"Result: {res}")

if __name__ == "__main__":
    asyncio.run(test_write())
