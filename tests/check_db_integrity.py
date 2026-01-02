import asyncio
import logging
from agent_runner.memory_server import MemoryServer
from agent_runner.state import AgentState

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_db():
    try:
        state = AgentState()
        mem = MemoryServer(state)
        await mem.ensure_connected()
        
        logger.info("Checking Database Integrity...")
        res = await mem.optimize_memory()
        
        if res.get("ok"):
            logger.info(f"DB Integrity Check: PASSED\nDetails: {res.get('info')}")
            
            # Also get stats
            stats = await mem.get_memory_stats()
            logger.info(f"DB Stats: {stats}")
        else:
            logger.error(f"DB Integrity Check: FAILED\nError: {res.get('error')}")

    except Exception as e:
        logger.error(f"Script Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
