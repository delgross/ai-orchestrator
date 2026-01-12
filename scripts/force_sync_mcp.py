import asyncio
import logging
from agent_runner.service_registry import ServiceRegistry
from agent_runner.state import AgentState
from agent_runner.config_manager import ConfigManager

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("force_sync")

async def main():
    logger.info("Initializing State...")
    state = AgentState()
    # Initialize Memory Server connection explicitly
    from agent_runner.memory_server import MemoryServer
    memory = MemoryServer(state)
    await memory.initialize()
    state.memory_server = memory
    
    # We don't need full engine, just config manager
    manager = ConfigManager(state)
    
    logger.info("Forcing MCP Sync from Disk...")
    await manager.sync_mcp_from_disk()
    
    logger.info("Done.")

if __name__ == "__main__":
    asyncio.run(main())
