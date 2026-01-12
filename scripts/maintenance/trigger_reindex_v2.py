import asyncio
import sys
import logging
import os

# Init logging to file and stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("reindex_debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

sys.path.append("/Users/bee/Sync/Antigravity/ai")
from agent_runner.memory_server import MemoryServer

async def run():
    logger.info("Initializing MemoryServer...")
    try:
        ms = MemoryServer()
        await ms.initialize()
        
        logger.info("Triggering Reindex...")
        await ms.reindex_memory()
        logger.info("Reindex Complete.")
    except Exception as e:
        logger.error(f"CRITICAL ERROR: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run())
