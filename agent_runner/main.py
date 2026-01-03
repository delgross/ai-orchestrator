import asyncio
import logging
import time
import os
import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path

from common.logging_setup import setup_logger
from common.constants import OBJ_MODEL
from agent_runner.agent_runner import get_shared_state, get_shared_engine
from agent_runner.app import create_app
from agent_runner.location import get_location # [NEW]

# Global logger for startup/lifecycle
# Global logger for startup/lifecycle
setup_logger("common") # Capture library logs (Circuit Breaker, etc)
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
    await state.initialize()
    
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
        
        # 10-second timeout for internet check
        try:
            state.internet_available = await asyncio.wait_for(check_internet_connectivity(), timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Startup internet check timed out (10s). Assuming Offline.")
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

    # Initialize Memory Server (Internal Access) [Phase 13 fix]
    from agent_runner.memory_server import MemoryServer
    from agent_runner.registry import ServiceRegistry
    
    memory_server = MemoryServer()
    # Ensure it's connected (lazy init handled by class, but let's pre-warm)
    try:
        await memory_server.initialize()
        ServiceRegistry.register_memory_server(memory_server)
        logger.info("Internal MemoryServer registered.")
    except Exception as e:
        logger.warning(f"Failed to initialize internal MemoryServer: {e}")

    # Initialize Task Manager and Background Workers
    from agent_runner.background_tasks import get_task_manager
    tm = get_task_manager()
    await tm.start()

    # [PHASE 44] Fire-and-Forget System Ingestion
    from agent_runner.system_ingestor import SystemIngestor
    ingestor = SystemIngestor(state)
    asyncio.create_task(ingestor.run())
    logger.info("System Ingestion task triggered (Background).")
    
    # Load Dynamic Tasks from Config (pass in-memory config)
    from agent_runner.task_loader import register_tasks_from_config
    await register_tasks_from_config(tm, state.config, state)
    
    # [PHASE RAG] Unified Lifecycle: Start RAG Server as Subprocess
    # This ensures it is covered by the 'Safety Net' (atexit) and dies when Agent dies.
    import sys
    import subprocess
    from agent_runner.transports.stdio import _ACTIVE_SUBPROCESSES
    
    rag_port = 5555
    rag_script = Path(__file__).parent.parent / "rag_server.py"
    
    # Check if already running (to avoid conflict if manually started)
    # Simple check: try to connect? Or just assume we own it in Production.
    # For robustness, we spawn.
    logger.info(f"Spawning RAG Server (Unified Lifecycle) on port {rag_port}...")
    try:
        # Use same python interpreter as agent
        rag_proc = subprocess.Popen(
            [sys.executable, str(rag_script)],
            cwd=str(rag_script.parent),
            stdout=subprocess.DEVNULL, # Redirect logs or keep them?
            stderr=subprocess.DEVNULL  # For now silence to avoid clutter, logs go to file in script?
            # actually rag_server logs to console usually. 
        )
        _ACTIVE_SUBPROCESSES.add(rag_proc)
        logger.info(f"RAG Server spawned with PID {rag_proc.pid}")
        state.rag_process = rag_proc # Keep ref
    except Exception as e:
        logger.error(f"Failed to spawn RAG server: {e}")

    # [PHASE RAG] Start RAG Ingestor Watchdog
    from agent_runner.rag_ingestor import start_rag_watcher
    # Use config or default
    rag_url = state.config.get("mcp_servers", {}).get("rag", {}).get("url", f"http://127.0.0.1:{rag_port}")
    try:
        start_rag_watcher(rag_url, state)
    except Exception as e:
        logger.error(f"Failed to start RAG Watchdog: {e}")

    try:
        # [NEW] Log Sorter Service (Micro-batch Classifier)
        from agent_runner.services.log_sorter import LogSorterService
        # Fix: LogSorterService.__init__ only takes config, state helps if injected separately or if init changed.
        # Checking definition: def __init__(self, config): ...
        # So we should only pass config.
        sorter = LogSorterService(state.config)
        # If state injection is needed (it is used in _perform_llm_analysis for dynamic model), we set it after.
        sorter.state = state
        await sorter.start()
        state.log_sorter = sorter # Persist in state for shutdown or access
        logger.info("Log Sorter Service started.")
    except Exception as e:
        logger.critical(f"CRITICAL STARTUP FAILURE in LogSorter: {e}", exc_info=True)
        # We don't want to kill the whole agent if Sorter fails, but we need to know.

    try:
        logger.info("Agent Runner Lifecycle Initialized.")
    except Exception:
        pass

async def on_shutdown():
    """System shutdown routines."""
    logger.info("Stopping Agent Runner services...")
    from agent_runner.background_tasks import get_task_manager
    await get_task_manager().stop()
    
    # [NEW] Stop Log Sorter
    if hasattr(state, 'log_sorter'):
        await state.log_sorter.stop()
    
    # [FIX] Ensure MCP subprocesses are killed to prevent orphans
    logger.info("Cleaning up MCP processes...")
    await state.cleanup_all_stdio_processes()
    
    logger.info("Cleanup complete.")

# Initialize the modularized FastAPI app
app = create_app()

# Attach lifespan
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5460))
    uvicorn.run("agent_runner.main:app", host="127.0.0.1", port=port, reload=True)
