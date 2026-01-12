
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seo_update")

async def main():
    state = AgentState()
    memory = MemoryServer(state)
    await memory.initialize()
    
    logger.info("🔧 Applying SEO Fix to Time Tool...")
    
    # 1. Update 'get_current_time'
    new_desc = "Get the precise current wall-clock time, date, and timezone for the user in a human-readable format. Use this whenever the user asks for the time."
    query = f"UPDATE tool_definition SET description = '{new_desc}' WHERE name = 'get_current_time'"
    
    try:
        await memory._execute_query(query)
        logger.info("✅ Updated 'get_current_time' description.")
    except Exception as e:
        logger.error(f"❌ Failed to update time tool: {e}")

    # 2. Verify
    verify = await memory._execute_query("SELECT description FROM tool_definition WHERE name = 'get_current_time'")
    logger.info(f"New Description: {verify[0]['description']}")

if __name__ == "__main__":
    asyncio.run(main())
