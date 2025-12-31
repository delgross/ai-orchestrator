
import logging
from agent_runner.agent_runner import get_shared_engine

logger = logging.getLogger("agent_runner.mcp_tasks")

async def mcp_refresh_task():
    """
    Periodic Task: MCP Tool Check
    Refreshes the list of available tools from all connected MCP servers.
    This ensures that if a server updates or comes online, the system
    becomes 'aware' of its functions without a restart.
    """
    logger.info("🔄 MCP Refresh: Checking for tool updates...")
    try:
        engine = get_shared_engine()
        await engine.discover_mcp_tools()
        logger.info("✅ MCP Refresh: Tool registry updated.")
    except Exception as e:
        logger.error(f"❌ MCP Refresh Failed: {e}", exc_info=True)
