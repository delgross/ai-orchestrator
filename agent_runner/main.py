import asyncio
import json
import logging
import time
import os
import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI

from common.logging_setup import setup_logger
from agent_runner.service_registry import ServiceRegistry
from agent_runner.state import AgentState
from agent_runner.engine import AgentEngine
from agent_runner.system_ingestor import SystemIngestor
from agent_runner.location import get_location
from agent_runner.memory_client import create_memory_client

# Global logger for startup/lifecycle
setup_logger("common") # Capture library logs (Circuit Breaker, etc)

# Pydantic AI Integration - Phase 1: Observability
try:
    import logfire
    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False
    logfire = None
setup_logger("agent_runner")
logger = logging.getLogger("agent_runner")

# Initialize Service Registry first
def _ensure_core_services():
    """Ensure state and engine are registered and available."""
    try:
        return ServiceRegistry.get_state(), ServiceRegistry.get_engine()
    except RuntimeError:
        # First time initialization - skip memory init to avoid import-time DB connections
        _state = AgentState(skip_memory_init=True)
        ServiceRegistry.register_state(_state)

        # For now, create engine with None memory_client - it will be set during startup
        # The actual memory client creation happens in on_startup after state.initialize()
        _engine = AgentEngine(_state, None)
        ServiceRegistry.register_engine(_engine)
        return _state, _engine

# Global state and engine are initialized in lifespan handler
state = None
engine = None

@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for startup and shutdown routines."""
    # 1. Startup Logic
    global state, engine
    state, engine = _ensure_core_services()
    await on_startup()
    yield
    # 2. Shutdown Logic
    await on_shutdown()

async def _clear_chat_window(state):
    """Clear the chat window before startup messages."""
    # This is a no-op for now - can be implemented if needed
    pass


async def _send_startup_monitor_message(state, message: str):
    """Send a startup monitor message."""
    logger.info(message)
    # Could send to UI or monitoring system if implemented
    pass


async def _send_startup_status_to_chat(state, startup_issues, startup_warnings, total_duration):
    """Send startup status to chat interface."""
    # This could send a message to the chat interface about startup completion
    # For now, just log it
    logger.info(f"Startup completed in {total_duration:.2f}s with {len(startup_issues)} issues and {len(startup_warnings)} warnings")


async def _clear_python_cache():
    """Clear Python bytecode cache if requested."""
    if os.getenv("CLEAR_CACHE_ON_STARTUP", "false").lower() != "true":
        return

    logger.info("🧹 Clearing Python bytecode cache...")
    import shutil

    cache_dirs = []
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__':
                cache_dirs.append(os.path.join(root, d))

    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            logger.debug(f"Cleared cache: {cache_dir}")
        except Exception as e:
            logger.debug(f"Failed to clear {cache_dir}: {e}")

    # Clear .pyc files
    import glob
    pyc_files = glob.glob('**/*.pyc', recursive=True)
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            logger.debug(f"Removed .pyc: {pyc_file}")
        except Exception as e:
            logger.debug(f"Failed to remove {pyc_file}: {e}")

    logger.info(f"✅ Cleared {len(cache_dirs)} cache directories and {len(pyc_files)} .pyc files")


async def _validate_startup_requirements():
    """Validate startup dependencies and environment."""
    step_start = time.time()
    await _send_startup_monitor_message(state, "🚀 Starting system initialization...")

    try:
        from agent_runner.startup_validator import validate_startup_dependencies
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        validation_errors, validation_warnings = await validate_startup_dependencies(project_root)

        if validation_errors:
            error_msg = f"Startup validation failed with {len(validation_errors)} critical errors"
            logger.error(f"❌ {error_msg}")
            for error in validation_errors:
                logger.error(f"  - {error}")
            return False, validation_errors

        if validation_warnings:
            for warning in validation_warnings:
                logger.warning(f"⚠️ {warning}")

        step_duration = time.time() - step_start
        logger.info(f"[BOOT_STEP] 0/8 Complete: {len(validation_warnings)} warnings (took {step_duration:.2f}s)")
        return True, []
    except Exception as e:
        step_duration = time.time() - step_start
        logger.error(f"[BOOT_STEP] 0/8 Validation failed after {step_duration:.2f}s: {e}", exc_info=True)
        return False, [str(e)]


async def _initialize_system_state():
    """Initialize the core system state."""
    step_start = time.time()
    await _send_startup_monitor_message(state, "🔄 Initializing system state...")

    try:
        await state.initialize()
        step_duration = time.time() - step_start
        logger.info(f"[BOOT_STEP] 1/8 Complete in {step_duration:.2f}s")
        logger.info(f"State initialized: memory={'✅' if state.memory else '❌'}, config={len(state.config)} keys, modes={len(state.modes)}")

        # Set system start time for staggered health checks
        state.system_start_time = time.time()

        # Inject startup message into event queue (will be picked up by Nexus)
        if not hasattr(state, 'system_event_queue'):
            state.system_event_queue = asyncio.Queue()

        await state.system_event_queue.put({
            "event": {
                "type": "system_status",
                "content": "The system may experience slight delays in the first minute for system tuning.",
                "severity": "info"
            },
            "request_id": None,
            "timestamp": time.time()
        })

        await _send_startup_monitor_message(state, f"✅ State initialized ({step_duration:.1f}s)")
        return True

    except Exception as e:
        step_duration = time.time() - step_start
        logger.error(f"[BOOT_STEP] 1/8 Failed after {step_duration:.2f}s: {e}", exc_info=True)
        state.degraded_mode = True
        if not hasattr(state, 'degraded_reasons'):
            state.degraded_reasons = []
        state.degraded_reasons.append("state_init_failed")
        logger.warning("⚠️ Continuing in degraded mode - some features may be unavailable")
        return False


async def _initialize_intent_cache():
    """Pre-compute Maître d' intent classifications for common queries."""
    step_start = time.time()
    await _send_startup_monitor_message(state, "🧠 Pre-computing Maître d' intents...")

    try:
        from agent_runner.intent import precompute_common_intents
        from agent_runner.executor import ToolExecutor

        # Create executor to get tool menu
        executor = ToolExecutor(state)
        tool_menu = executor.get_core_menu()

        await precompute_common_intents(state, tool_menu)

        step_duration = time.time() - step_start
        logger.info(f"[BOOT_STEP] Intent Cache Complete in {step_duration:.2f}s")
        await _send_startup_monitor_message(state, f"✅ Maître d' intents cached ({step_duration:.1f}s)")
        return True

    except Exception as e:
        step_duration = time.time() - step_start
        logger.error(f"[BOOT_STEP] Intent Cache Failed after {step_duration:.2f}s: {e}", exc_info=True)
        await _send_startup_monitor_message(state, f"⚠️ Intent cache failed ({step_duration:.1f}s)")
        return False


async def _initialize_memory_server():
    """Initialize the memory server and database connection."""
    step_start = time.time()
    await _send_startup_monitor_message(state, "🔄 Connecting to database...")

    from agent_runner.service_registry import ServiceRegistry

    # state.initialize() already created memory server, just ensure it's initialized
    if state.memory is None:
        logger.warning("Memory server not found in state - creating new instance")
        from agent_runner.memory_server import MemoryServer
        state.memory = MemoryServer(state)

    # Check database readiness
    db_ready = False
    db_check_url = state.memory.url.replace("/sql", "/health")
    for check_attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=2.0) as check_client:
                health_resp = await check_client.get(db_check_url)
                if health_resp.status_code == 200:
                    db_ready = True
                    break
        except Exception:
            if check_attempt < 2:
                await asyncio.sleep(0.5)
                continue

    if not db_ready:
        logger.warning("Database health check failed - will attempt initialization anyway")

    try:
        await state.memory.initialize()

        # Verify connection stability
        memory_stable = False
        for check_round in range(5):
            try:
                test_result = await state.memory._execute_query("INFO FOR DB;")
                if test_result is not None:
                    memory_stable = True
                    if check_round > 0:
                        logger.info(f"Memory server stabilized after {check_round + 1} checks")
                    break
            except Exception as e:
                logger.debug(f"Memory stability check {check_round + 1} failed: {e}")
                if check_round < 4:
                    await asyncio.sleep(0.2)

        if not memory_stable:
            logger.warning("Memory server connection unstable - enabling recovery mode")
            state.memory_unstable = True

        try:
            ServiceRegistry.register_memory_server(state.memory)
        except Exception as reg_err:
            logger.warning(f"ServiceRegistry registration failed: {reg_err}")

        step_duration = time.time() - step_start
        stability_status = "stable" if memory_stable else "unstable"
        logger.info(f"[BOOT_STEP] 2/8 Complete in {step_duration:.2f}s")
        logger.info(f"MemoryServer connected: initialized={'✅' if state.memory.initialized else '❌'}, stability={stability_status}")
        await _send_startup_monitor_message(state, f"✅ Database connected ({step_duration:.1f}s, {stability_status})")
        return True
    except Exception as e:
        step_duration = time.time() - step_start
        logger.error(f"[BOOT_STEP] 2/8 Failed after {step_duration:.2f}s: {e}", exc_info=True)
        state.memory = None
        if not hasattr(state, 'degraded_features'):
            state.degraded_features = []
        state.degraded_features.append("memory")
        logger.warning("⚠️ Continuing without memory features - memory-dependent functionality will be disabled")

        # Attempt background recovery
        from agent_runner.memory_recovery import start_memory_recovery_if_needed
        await start_memory_recovery_if_needed(state)
        return False


async def _initialize_network_and_location():
    """Initialize network connectivity and location detection."""
    try:
        from agent_runner.health_monitor import check_internet_connectivity, initialize_health_monitor
        client = await state.get_http_client()

        # Gather location
        location_start = time.time()
        try:
            state.location = await asyncio.wait_for(get_location(state.config, memory=state.memory), timeout=2.0)
            location_duration = time.time() - location_start
            logger.info(f"Location detected: {state.location.get('city', 'Unknown')} (took {location_duration:.2f}s, source: {state.location.get('source', 'unknown')})")
        except asyncio.TimeoutError:
            logger.warning("Startup location check timed out (2s). Using generic fallback.")
            state.location = {
                "city": "Unknown", "region": "Unknown", "country": "Unknown",
                "postal_code": "", "lat": 0.0, "lon": 0.0, "timezone": "UTC",
                "source": "timeout_fallback"
            }
        except Exception as e:
            logger.warning(f"Startup location check failed: {e}. Using generic fallback.")
            state.location = {
                "city": "Unknown", "region": "Unknown", "country": "Unknown",
                "postal_code": "", "lat": 0.0, "lon": 0.0, "timezone": "UTC",
                "source": "error_fallback"
            }

        initialize_health_monitor(state.mcp_servers, state.mcp_circuit_breaker, state.gateway_base, client, state)

        # Background internet check
        async def background_internet_check():
            try:
                logger.info("Starting background internet connectivity check...")
                is_online = await check_internet_connectivity()
                state.internet_available = is_online
                status = "✅ Online" if is_online else "❌ Offline"
                logger.info(f"Background Internet Check Result: {status}")
                if not is_online:
                    logger.warning("System transitioned to Offline Mode.")
            except Exception as e:
                logger.error(f"Background internet check failed: {e}")
                state.internet_available = False

        asyncio.create_task(background_internet_check())
        logger.info("Internet check dispatched to background (Optimistic: Online)")
        return True
    except Exception as e:
        logger.warning(f"Network/location initialization error: {e}")
        return False


async def _load_mcp_servers():
    """Load and discover MCP servers."""
    mcp_start = time.time()
    mcp_failed_servers = []

    try:
        await _send_startup_monitor_message(state, "🔄 Loading MCP servers...")

        # Reset MCP servers to enabled in database
        if hasattr(state, "memory") and state.memory:
            try:
                from agent_runner.db_utils import run_query
                await run_query(state, "UPDATE mcp_server SET enabled = true WHERE disabled_reason != 'user_request_redundant' OR disabled_reason IS NULL;")
                logger.info("🔄 Reset all MCP servers to enabled for fresh discovery attempt")
            except Exception as e:
                logger.warning(f"Failed to reset MCP server enabled flags: {e}")

        from agent_runner.config import load_mcp_servers
        await load_mcp_servers(state)
        logger.info(f"Loaded {len(state.mcp_servers)} MCP server configs. Starting discovery...")
        await _send_startup_monitor_message(state, f"🔍 Discovering {len(state.mcp_servers)} MCP servers...")
        await engine.discover_mcp_tools()

        mcp_duration = time.time() - mcp_start
        total_tools = sum(len(tools) for tools in engine.executor.mcp_tool_cache.values())

        # Track failed servers
        from agent_runner.constants import CORE_MCP_SERVERS
        core_failed_servers = []
        non_core_failed_servers = []

        for server_name, cfg in state.mcp_servers.items():
            if not cfg.get("enabled", True):
                if server_name not in engine.executor.mcp_tool_cache:
                    if server_name in CORE_MCP_SERVERS:
                        core_failed_servers.append(server_name)
                    else:
                        non_core_failed_servers.append(server_name)

        logger.info(f"MCP Discovery complete: {len(engine.executor.mcp_tool_cache)}/{len(state.mcp_servers)} servers, {total_tools} tools (took {mcp_duration:.2f}s)")
        await _send_startup_monitor_message(state, f"✅ MCP Discovery: {len(engine.executor.mcp_tool_cache)}/{len(state.mcp_servers)} servers, {total_tools} tools ({mcp_duration:.1f}s)")

        # Index tools in database
        if hasattr(engine, 'executor') and hasattr(state, 'memory') and state.memory:
            try:
                all_tool_defs = engine.executor.tool_definitions
                index_result = await state.memory.index_tools(all_tool_defs)
                if index_result.get("ok"):
                    logger.info(f"Indexed {index_result.get('indexed', 0)} tools in database for semantic search")
            except Exception as e:
                logger.warning(f"Tool indexing failed: {e}")

        return core_failed_servers, non_core_failed_servers

    except Exception as e:
        logger.error(f"MCP server loading failed: {e}")
        return [], []


async def _initialize_task_manager():
    """Initialize the background task manager."""
    step_start = time.time()
    await _send_startup_monitor_message(state, "🔄 Starting background tasks...")

    try:
        from agent_runner.background_tasks import get_task_manager
        tm = get_task_manager()
        await tm.start()
        step_duration = time.time() - step_start
        task_count = len(tm.tasks) if hasattr(tm, 'tasks') else 0
        logger.info(f"Task Manager started: {task_count} tasks registered")
        logger.info(f"[BOOT_STEP] 4/8 Complete in {step_duration:.2f}s")
        await _send_startup_monitor_message(state, f"✅ Background tasks started: {task_count} tasks ({step_duration:.1f}s)")
        return True
    except Exception as e:
        step_duration = time.time() - step_start
        logger.error(f"[BOOT_STEP] 4/8 Failed after {step_duration:.2f}s: {e}", exc_info=True)
        logger.warning("⚠️ Continuing without background tasks - scheduled tasks will not run")
        return False


async def _initialize_system_ingestion():
    """Initialize system ingestion and configuration loading."""
    step_start = time.time()
    await _send_startup_monitor_message(state, "🔄 Loading system configuration...")

    try:
        from agent_runner.system_ingestor import SystemIngestor
        ingestor = SystemIngestor(state)

        async def ingestion_wrapper():
            try:
                state.ingestion_status["status"] = "running"
                state.ingestion_status["error"] = None
                await ingestor.run()
                state.ingestion_status["status"] = "completed"
                state.ingestion_status["completed"] = True
                logger.info("✅ System ingestion completed successfully")
            except asyncio.CancelledError:
                logger.debug("System ingestion cancelled during shutdown")
                state.ingestion_status["status"] = "cancelled"
                raise
            except Exception as e:
                logger.error(f"System ingestion task failed: {e}", exc_info=True)
                state.ingestion_status["status"] = "failed"
                state.ingestion_status["error"] = str(e)

        task = asyncio.create_task(ingestion_wrapper())
        logger.info("System Ingestion task triggered (Background).")

        # Load dynamic tasks from config
        try:
            from agent_runner.task_loader import register_tasks_from_config
            tm = None
            try:
                from agent_runner.background_tasks import get_task_manager
                tm = get_task_manager()
            except:
                pass

            if tm is not None:
                await register_tasks_from_config(tm, state.config, state)
        except Exception as task_err:
            logger.warning(f"Failed to register tasks from config: {task_err}")

        step_duration = time.time() - step_start
        logger.info(f"[BOOT_STEP] 5/8 Complete in {step_duration:.2f}s")
        await _send_startup_monitor_message(state, f"✅ System configuration loaded ({step_duration:.1f}s)")
        return True
    except Exception as e:
        logger.error(f"System ingestion setup failed: {e}")
        return False


async def _initialize_rag_services():
    """Initialize RAG server and related services."""
    step_start = time.time()
    await _send_startup_monitor_message(state, "🔄 Starting RAG services...")

    try:
        import sys
        import subprocess
        from agent_runner.transports.stdio import _ACTIVE_SUBPROCESSES

        rag_port = 5555
        rag_script = Path(__file__).parent.parent / "rag_server.py"

        # Check if already running
        from common.port_utils import port_in_use
        rag_running = port_in_use(rag_port)

        if rag_running:
            logger.info(f"RAG Server already running on port {rag_port}, skipping spawn")
            state.rag_process = None
        else:
            logger.info(f"Spawning RAG Server on port {rag_port}...")
            rag_proc = subprocess.Popen(
                [sys.executable, str(rag_script)],
                cwd=str(rag_script.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            _ACTIVE_SUBPROCESSES.add(rag_proc)
            logger.info(f"RAG Server spawned with PID {rag_proc.pid}")
            state.rag_process = rag_proc

            # Check if process started successfully
            await asyncio.sleep(0.5)
            if rag_proc.returncode is not None:
                logger.error(f"RAG Server process died immediately with exit code {rag_proc.returncode}")
                state.rag_process = None
            else:
                # Health check
                try:
                    import httpx
                    async with httpx.AsyncClient(timeout=2.0) as client:
                        resp = await client.get(f"http://127.0.0.1:{rag_port}/health")
                        if resp.status_code == 200:
                            logger.info("✅ RAG Server health check passed")
                        else:
                            logger.warning(f"⚠️ RAG Server health check returned {resp.status_code}")
                except Exception as e:
                    logger.warning(f"⚠️ RAG Server health check failed: {e}")

        # Start RAG ingestor watchdog
        from agent_runner.rag_ingestor import start_rag_watcher, INGEST_DIR
        rag_url = state.config.get("mcp_servers", {}).get("rag", {}).get("url", f"http://127.0.0.1:{rag_port}")
        try:
            watcher = start_rag_watcher(rag_url, state)
            if watcher:
                logger.info(f"RAG Watchdog started: watching {INGEST_DIR}")
            else:
                logger.warning("RAG Watchdog not started (watchdog not available)")
        except Exception as e:
            logger.error(f"Failed to start RAG Watchdog: {e}", exc_info=True)

        step_duration = time.time() - step_start
        logger.info(f"[BOOT_STEP] 6/8 Complete in {step_duration:.2f}s")
        await _send_startup_monitor_message(state, f"✅ RAG services {'started' if not rag_running else 'unavailable'} ({step_duration:.1f}s)")
        return True
    except Exception as e:
        step_duration = time.time() - step_start
        logger.error(f"RAG services initialization failed: {e}")
        return False


async def _validate_registry_integrity():
    """Validate system registry integrity."""
    step_start = time.time()
    logger.info("[BOOT_STEP] 7/7 Registry Validation")
    await _send_startup_monitor_message(state, "🔄 Validating registry integrity...")

    try:
        from agent_runner.maintenance_tasks import validate_registry_integrity
        validation_result = await validate_registry_integrity(state)
        if not validation_result.get("ok"):
            issues = validation_result.get("issues", [])
            warnings = validation_result.get("warnings", [])
            if issues:
                logger.warning(f"Registry validation found {len(issues)} issues: {issues}")
            if warnings:
                logger.info(f"Registry validation found {len(warnings)} warnings: {warnings}")
        else:
            logger.info("Registry validation passed")
    except Exception as e:
        logger.warning(f"Registry validation failed: {e}", exc_info=True)

    logger.info(f"[BOOT_STEP] 7/7 Complete in {time.time() - step_start:.2f}s")
    await _send_startup_monitor_message(state, f"✅ Registry validated ({time.time() - step_start:.1f}s)")


async def on_startup():
    """System startup routines - refactored into focused phases."""
    startup_start = time.time()
    logger.info("🚀 Starting Agent Runner initialization...")

    # Track startup issues and warnings
    startup_issues = []
    startup_warnings = []

    # Clear chat window before startup messages
    await _clear_chat_window(state)

    # Phase 1: Cache clearing (if requested)
    await _clear_python_cache()

    # Phase 2: Startup validation
    validation_ok, validation_issues = await _validate_startup_requirements()
    if validation_issues:
        startup_issues.extend(validation_issues)

    # Phase 3: State initialization
    state_ok = await _initialize_system_state()
    if not state_ok:
        startup_issues.append("State initialization failed")

    # Create memory client now that state is initialized
    from agent_runner.memory_client import create_memory_client
    memory_client = create_memory_client(state, {"memory_mode": getattr(state, 'memory_mode', 'direct')})
    logger.info(f"Initialized memory client: {type(memory_client).__name__}")
    engine.memory_client = memory_client

    # Initialize async components that require running event loop
    await engine.async_initialize()

    # Phase 4: Memory server initialization
    memory_ok = await _initialize_memory_server()
    if not memory_ok:
        startup_warnings.append("Memory server initialization failed")

    # Phase 5: Network and location initialization
    network_ok = await _initialize_network_and_location()
    if not network_ok:
        startup_warnings.append("Network/location initialization failed")

    # Phase 6: MCP server loading and discovery
    core_failed, non_core_failed = await _load_mcp_servers()
    if core_failed:
        error_msg = f"CRITICAL: Core MCP service(s) failed: {', '.join(core_failed)}. System functionality severely degraded."
        logger.error(error_msg)
        startup_issues.append(error_msg)

    if non_core_failed:
        warning_msg = f"MCP Discovery: {len(non_core_failed)} non-core servers failed: {', '.join(non_core_failed)}"
        logger.warning(warning_msg)
        startup_warnings.append(warning_msg)

    # Phase 7: Intent cache pre-computation
    intent_ok = await _initialize_intent_cache()
    if not intent_ok:
        startup_warnings.append("Intent cache pre-computation failed")

    # Phase 8: Task manager initialization
    task_ok = await _initialize_task_manager()
    if not task_ok:
        startup_warnings.append("Task manager initialization failed")

    # Phase 8: System ingestion
    ingestion_ok = await _initialize_system_ingestion()
    if not ingestion_ok:
        startup_warnings.append("System ingestion initialization failed")

    # Phase 9: RAG services
    rag_ok = await _initialize_rag_services()
    if not rag_ok:
        startup_warnings.append("RAG services initialization failed")

    # Phase 10: Registry validation
    await _validate_registry_integrity()

    # Startup completion
    total_duration = time.time() - startup_start
    logger.info(f"✅ Agent Runner initialization complete in {total_duration:.2f}s")

    # Determine overall health
    critical_issues = len(startup_issues)
    warnings = len(startup_warnings)

    if critical_issues > 0:
        status_message = f"⚠️ Startup completed with {critical_issues} critical issues and {warnings} warnings"
        logger.warning(status_message)
    else:
        status_message = f"✅ Startup completed successfully ({warnings} warnings)"
        logger.info(status_message)

    # Store startup status in database if possible
    try:
        if hasattr(state, 'memory') and state.memory and state.memory.initialized:
            from agent_runner.db_utils import run_query
            await run_query(
                state,
                "CREATE startup_status SET message = $msg, timestamp = time::now(), duration = $dur, issues = $issues, warnings = $warnings",
                {
                    "msg": status_message,
                    "dur": total_duration,
                    "issues": startup_issues,
                    "warnings": startup_warnings
                }
            )
            logger.debug("Startup status stored in database")
    except Exception as db_err:
        logger.debug(f"Could not store startup status in database: {db_err}")

    # Send final status to chat (best effort)
    try:
        await _send_startup_status_to_chat(
            state,
            startup_issues,
            startup_warnings,
            total_duration
        )
    except Exception as e:
        logger.warning(f"Error sending startup status to chat: {e}", exc_info=True)


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    app = FastAPI(title="Agent Runner", lifespan=lifespan)

    # Enable CORS for Browser Access
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routes
    from agent_runner.routes import chat, admin, mcp, server, files
    app.include_router(chat.router, prefix="/v1", tags=["chat"])
    app.include_router(admin.router, prefix="/admin", tags=["admin"])
    app.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
    app.include_router(server.router, prefix="/system", tags=["system"]) # Assuming server.py has router
    app.include_router(files.router, prefix="/files", tags=["files"])

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "agent_runner", "ok": True}  # Router expects "ok" field

    return app


# Create the FastAPI application instance
app = create_app()


async def on_shutdown():
    """System shutdown routines."""
    logger.info("Stopping Agent Runner services...")
    from agent_runner.background_tasks import get_task_manager
    await get_task_manager().stop()

    # [NEW] Stop Log Sorter
    if hasattr(state, 'log_sorter'):
        await state.log_sorter.stop()

    # Ensure MCP subprocesses are killed to prevent orphans
    logger.info("Cleaning up MCP processes...")
    await state.cleanup_all_stdio_processes()

    logger.info("Cleanup complete.")


# FastAPI app is already created above with create_app()
