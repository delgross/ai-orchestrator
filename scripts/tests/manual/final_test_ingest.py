import asyncio
import sys
import logging
import os

# Configure logging to stderr
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
log = logging.getLogger("test")

# EXPLICIT CONFIG
os.environ["SURREAL_URL"] = "http://127.0.0.1:8000/sql"
os.environ["SURREAL_USER"] = "root"
os.environ["SURREAL_PASS"] = "root"
os.environ["SURREAL_NS"] = "orchestrator"
os.environ["SURREAL_DB"] = "memory"

sys.path.append("/Users/bee/Sync/Antigravity/ai")
from agent_runner.memory_server import MemoryServer

async def run():
    log.info("Starting MemoryServer Test...")
    ms = MemoryServer()
    await ms.initialize()
    
    log.info("Storing Fact...")
    # NOTE: "confidence" kwarg was missing in my previous manual read, 
    # but store_fact signature has it.
    res = await ms.store_fact("Test", "is_working", "True", context="Final Verified", confidence=1.0)
    log.info(f"Store Result: {res}")

if __name__ == "__main__":
    asyncio.run(run())
