
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
logger = logging.getLogger("audit_tools")

async def main():
    state = AgentState()
    memory = MemoryServer(state)
    await memory.initialize()
    
    # Query tool definitions
    # We want to compare 'time' related tools vs 'search' related tools
    logger.info("🔍 Auditing Tool Descriptions...")
    
    # Get all tools
    # Assuming 'tool_definition' has 'name', 'description'
    try:
        # We can't do LIKE in Surreal easily on all fields without FULLTEXT index, 
        # so let's just fetch all and filter in python for this audit script
        query = "SELECT name, description, server FROM tool_definition"
        results = await memory._execute_query(query)
        
        time_tools = []
        search_tools = []
        
        for tool in results:
            name = tool.get("name", "").lower()
            desc = tool.get("description", "")
            server = tool.get("server", "")
            
            # Categorize
            if "time" in name or "date" in name or "clock" in name:
                time_tools.append(tool)
            elif "search" in name or "google" in name or "tavily" in name or "exa" in name:
                search_tools.append(tool)
                
        logger.info(f"\n--- TIME TOOLS ({len(time_tools)}) ---")
        for t in time_tools:
            logger.info(f"[{t['server']}] {t['name']}:\n    \"{t['description']}\"")
            
        logger.info(f"\n--- SEARCH TOOLS ({len(search_tools)}) ---")
        for t in search_tools:
            logger.info(f"[{t['server']}] {t['name']}:\n    \"{t['description']}\"")
            
    except Exception as e:
        logger.error(f"Failed to query tools: {e}")

if __name__ == "__main__":
    asyncio.run(main())
