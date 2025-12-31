import asyncio
import logging
import time
import os
import uvicorn
from contextlib import asynccontextmanager

from common.logging_setup import setup_logger
from common.constants import OBJ_MODEL
from agent_runner.agent_runner import get_shared_state, get_shared_engine
from agent_runner.app import create_app
from agent_runner.location import get_location # [NEW]

# Global logger for startup/lifecycle
setup_logger("agent_runner")
logger = logging.getLogger("agent_runner")

state = get_shared_state()
engine = get_shared_engine()

@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for startup and shutdown routines."""
    # 1. Startup Logic
    await on_startup()
    yield
    # 2. Shutdown Logic
    await on_shutdown()

async def on_startup():
    """System startup routines."""
    logger.info("Initializing Agent Runner (Modularized Strategy)...")
    
    # Check if internet is available for cloud models
    try:
        # Use the robust multi-target check from health monitor
        from agent_runner.health_monitor import check_internet_connectivity, initialize_health_monitor
        
        # USE PERSISTENT SHARED CLIENT from state for INTERNAL service checks (Dashboard, Gateway)
        # Internet checks will now use their own isolated client.
        client = await state.get_http_client()
        
        # [NEW] Gather Location (Once)
        try:
            # 2-second timeout for location to prevent hang
            state.location = await asyncio.wait_for(get_location(state.config), timeout=2.0)
        except asyncio.TimeoutError:
            logger.warning("Startup location check timed out (2s). Defaulting to Unknown.")
            state.location = {"source": "timeout", "city": "Unknown"}
        except Exception as e:
            logger.warning(f"Startup location check failed: {e}")
            state.location = {"source": "error", "city": "Unknown"}

        initialize_health_monitor(state.mcp_servers, state.mcp_circuit_breaker, state.gateway_base, client, state)
        
        # 3-second timeout for internet check
        try:
            state.internet_available = await asyncio.wait_for(check_internet_connectivity(), timeout=3.0)
        except asyncio.TimeoutError:
            logger.warning("Startup internet check timed out (3s). Assuming Offline.")
            state.internet_available = False
        # Do NOT close client here, it's owned by State
    except Exception as e:
        logger.warning(f"Startup internet check failed: {e}")
        state.internet_available = False
    
    if not state.internet_available:
        logger.warning("Internet access unavailable. Cloud models will be DISABLED.")
    
    # Load and Discover MCP Servers
    try:
        from agent_runner.config import load_mcp_servers
        await load_mcp_servers(state)
        await engine.discover_mcp_tools()
        logger.info(f"Loaded {len(state.mcp_servers)} MCP servers.")
    except Exception as e:
        logger.error(f"Failed to load MCP servers during startup: {e}")

    # Initialize Notifications Configuration
    from common.notifications import get_notification_manager
    alert_path = state.config.get("system", {}).get("alert_file_path")
    if alert_path:
        get_notification_manager().configure(alert_file_path=alert_path)

    # Initialize Task Manager and Background Workers
    from agent_runner.background_tasks import get_task_manager
    tm = get_task_manager()
    await tm.start()
    
    # Register core tasks
    # (Moved to file-based scheduler: see agent_runner/tasks/definitions/)
    # from agent_runner.memory_tasks import memory_backup_task, memory_consolidation_task
    # from agent_runner.maintenance_tasks import daily_research_task
    
    # tm.register("memory_backup", memory_backup_task, interval=3600*12) 
    # tm.register("consolidator", memory_consolidation_task, interval=3600*24)
    # tm.register("daily_research", daily_research_task, interval=3600*24)

    # Load Dynamic Tasks from Config (pass in-memory config)
    from agent_runner.task_loader import register_tasks_from_config
    register_tasks_from_config(tm, state.config)
    
    logger.info("Agent Runner Lifecycle Initialized.")

async def on_shutdown():
    """System shutdown routines."""
    logger.info("Stopping Agent Runner services...")
    from agent_runner.background_tasks import get_task_manager
    await get_task_manager().stop()
    logger.info("Cleanup complete.")

# Initialize the modularized FastAPI app
app = create_app()

# Attach lifespan
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5460))
    uvicorn.run("agent_runner.main:app", host="0.0.0.0", port=port, reload=True)
