
import logging
from agent_runner.agent_runner import get_shared_engine

logger = logging.getLogger("agent_runner.mcp_tasks")

async def mcp_refresh_task():
    """
    Periodic Task: MCP Tool Check
    Refreshes the list of available tools from all connected MCP servers.
    This ensures that if a server updates or comes online, the system
    becomes 'aware' of its functions without a restart.
    
    [FIX] Only refreshes tools for servers that are already enabled and working.
    Does NOT attempt to rediscover failed servers (which would disable them).
    """
    logger.info("🔄 MCP Refresh: Checking for tool updates...")
    try:
        engine = get_shared_engine()
        state = engine.state
        
        # [FIX] Only refresh tools for servers that are already enabled and have tools cached
        # This prevents the refresh from disabling servers that are temporarily unavailable
        enabled_servers = [
            name for name, cfg in state.mcp_servers.items() 
            if cfg.get("enabled", True) and name in engine.executor.mcp_tool_cache
        ]
        
        if not enabled_servers:
            logger.debug("MCP Refresh: No enabled servers with cached tools to refresh")
            return
        
        logger.info(f"MCP Refresh: Refreshing tools for {len(enabled_servers)} enabled servers...")
        
        # Refresh tools for each enabled server individually (non-destructive)
        refreshed_count = 0
        for server_name in enabled_servers:
            try:
                cfg = state.mcp_servers[server_name]
                # Use a non-destructive discovery that won't disable on failure
                success = await engine.executor._discover_single_server(
                    server_name,
                    cfg,
                    attempt=1,
                    max_attempts=1,
                    disable_on_failure=False  # Non-destructive refresh
                )
                if success:
                    refreshed_count += 1
                else:
                    # Log but don't disable - server might be temporarily unavailable
                    logger.debug(f"MCP Refresh: Server '{server_name}' refresh failed (non-critical)")
            except Exception as e:
                logger.debug(f"MCP Refresh: Server '{server_name}' refresh exception (non-critical): {e}")
        
        logger.info(f"✅ MCP Refresh: Refreshed {refreshed_count}/{len(enabled_servers)} servers")
    except Exception as e:
        logger.error(f"❌ MCP Refresh Failed: {e}", exc_info=True)
