import asyncio
import sys
import logging
# Add project root to path
sys.path.append("/Users/bee/Sync/Antigravity/ai")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agent_runner.memory_server")
logger.setLevel(logging.DEBUG)

from agent_runner.memory_server import MemoryServer

async def test_write():
    print("Initializing MemoryServer...")
    ms = MemoryServer()
    try:
        await ms.initialize()
        print("Connected.")
        
        print("Attempting to store fact...")
        res = await ms.store_fact("TestEntity", "is_debugging", "True", context="Verbose Test", confidence=1.0)
        print(f"Result: {res}")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_write())
