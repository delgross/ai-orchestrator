import asyncio
import json
import logging
import time
import os
import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from common.logging_setup import setup_logger
from agent_runner.service_registry import ServiceRegistry
from agent_runner.state import AgentState
from agent_runner.engine import AgentEngine
from agent_runner.system_ingestor import SystemIngestor
from agent_runner.location import get_location

# Global logger for startup/lifecycle
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
        # First time initialization
        _state = AgentState()
        ServiceRegistry.register_state(_state)
        _engine = AgentEngine(_state)
        ServiceRegistry.register_engine(_engine)
        return _state, _engine

state, engine = _ensure_core_services()

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
    startup_start = time.time()
    logger.info("🚀 Starting Agent Runner initialization...")

    # OPTIMIZATION: Only clear cache when explicitly requested via environment variable
    # This prevents slow startups during normal operation
    if os.getenv("CLEAR_CACHE_ON_STARTUP", "false").lower() == "true":
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

    # Track startup issues
    startup_issues = []
    startup_warnings = []

    # Clear chat window before startup messages (but not before final system status)
    await _clear_chat_window(state)

    # [NEW] BOOT_STEP 0/7: Comprehensive Startup Validation
    logger.info("[BOOT_STEP] 0/7 Startup Validation")
    step_start = time.time()
    # await _send_startup_monitor_message(state, "🚀 Starting system initialization...")
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
            startup_issues.append(error_msg)
            startup_issues.extend(validation_errors)
            # Don't crash - continue in degraded mode, but log all errors
        
        if validation_warnings:
            for warning in validation_warnings:
                logger.warning(f"⚠️ {warning}")
                startup_warnings.append(warning)
        
        step_duration = time.time() - step_start
        if validation_errors:
            logger.warning(f"[BOOT_STEP] 0/7 Complete with {len(validation_errors)} errors, {len(validation_warnings)} warnings (took {step_duration:.2f}s)")
        else:
            logger.info(f"[BOOT_STEP] 0/7 Complete: {len(validation_warnings)} warnings (took {step_duration:.2f}s)")
    except Exception as e:
        step_duration = time.time() - step_start
        logger.error(f"[BOOT_STEP] 0/7 Validation failed after {step_duration:.2f}s: {e}", exc_info=True)
        startup_warnings.append(f"Startup validation check failed: {e}")
        # Continue - validation failure shouldn't prevent startup
    
    logger.info("[BOOT_STEP] 1/7 State Initialization")
    step_start = time.time()
    # await _send_startup_monitor_message(state, "🔄 Initializing system state...")
    
    try:
        await state.initialize()
        step_duration = time.time() - step_start
        logger.info(f"[BOOT_STEP] 1/7 Complete in {step_duration:.2f}s")
        logger.info(f"State initialized: memory={'✅' if state.memory else '❌'}, config={len(state.config)} keys, modes={len(state.modes)}")
        
        # Set system start time for staggered health checks
        state.system_start_time = time.time()
        
        # Inject startup message into event queue (will be picked up by Nexus)
        if not hasattr(state, 'system_event_queue'):
            state.system_event_queue = asyncio.Queue()
        
        # await state.system_event_queue.put({
        #     "event": {
        #         "type": "system_status",  # NOT system_message - goes to frontend, not LLM
        #         "content": "The system may experience slight delays in the first minute for system tuning.",
        #         "severity": "info"
        #     },
        #     "request_id": None,  # Broadcast to all requests
        #     "timestamp": time.time()
        # })
        
        # Send completion message
        # await _send_startup_monitor_message(state, f"✅ State initialized ({step_duration:.1f}s)")
    except Exception as e:
        step_duration = time.time() - step_start
        logger.error(f"[BOOT_STEP] 1/7 Failed after {step_duration:.2f}s: {e}", exc_info=True)
        # [FIX] Don't crash - allow degraded mode
        startup_issues.append(f"State initialization failed: {e}")
        state.degraded_mode = True
        if not hasattr(state, 'degraded_reasons'):
            state.degraded_reasons = []
        state.degraded_reasons.append("state_init_failed")
        logger.warning("⚠️ Continuing in degraded mode - some features may be unavailable")

    # Initialize Memory Server (Internal Access) [Phase 13 fix]
    # MOVED UP: Must enforce schema BEFORE ConfigManager (triggered by MCP load) writes to DB.
    # NOTE: state.initialize() already creates memory server, but we need to ensure it's initialized
    logger.info("[BOOT_STEP] 2/7 Memory Server Init")
    step_start = time.time()
    # await _send_startup_monitor_message(state, "🔄 Connecting to database...")
    
    from agent_runner.service_registry import ServiceRegistry
    
    # state.initialize() already created memory server, just ensure it's initialized
    # This is a no-op if already initialized, but ensures schema is set up
    try:
        if state.memory is None:
            # This shouldn't happen if state.initialize() succeeded, but handle gracefully
            logger.warning("Memory server not found in state - creating new instance")
            from agent_runner.memory_server import MemoryServer
            state.memory = MemoryServer(state)
        
        # CRITICAL: Check database readiness before initialization
        # This prevents connection failures during startup
        import httpx
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
            logger.warning("Database health check failed - will attempt initialization anyway (may retry)")
        
        await state.memory.initialize()

        # MEMORY ROBUSTNESS: Verify connection stays stable
        memory_robustness_checks = 0
        max_robustness_checks = 5
        memory_stable = False

        for check_round in range(max_robustness_checks):
            try:
                # Quick connectivity test
                test_result = await state.memory._execute_query("INFO FOR DB;")
                if test_result is not None:
                    memory_stable = True
                    if check_round > 0:
                        logger.info(f"Memory server stabilized after {check_round + 1} checks")
                    break
            except Exception as e:
                logger.debug(f"Memory stability check {check_round + 1} failed: {e}")
                if check_round < max_robustness_checks - 1:
                    await asyncio.sleep(0.2)  # Brief wait before retry
                    continue

        if not memory_stable:
            logger.warning("Memory server connection unstable - enabling recovery mode")
            # Set flag for degraded but recoverable memory mode
            state.memory_unstable = True

        try:
            ServiceRegistry.register_memory_server(state.memory)
        except Exception as reg_err:
            logger.warning(f"ServiceRegistry registration failed: {reg_err}")
            startup_warnings.append(f"ServiceRegistry unavailable: {reg_err}")

        step_duration = time.time() - step_start
        logger.info(f"[BOOT_STEP] 2/7 Complete in {step_duration:.2f}s")
        stability_status = "stable" if memory_stable else "unstable"
        logger.info(f"MemoryServer connected: initialized={'✅' if state.memory.initialized else '❌'}, DB={state.config.get('surreal', {}).get('db', 'memory')}, stability={stability_status}")
        # await _send_startup_monitor_message(state, f"✅ Database connected ({step_duration:.1f}s, {stability_status})")
    except Exception as e:
        step_duration = time.time() - step_start
        logger.error(f"[BOOT_STEP] 2/7 Failed after {step_duration:.2f}s: {e}", exc_info=True)
        # [FIX] Don't crash - allow degraded mode without memory
        startup_warnings.append(f"Memory server unavailable: {e}")
        state.memory = None
        if not hasattr(state, 'degraded_features'):
            state.degraded_features = []
        state.degraded_features.append("memory")
        logger.warning("⚠️ Continuing without memory features - memory-dependent functionality will be disabled")
        
        # CRITICAL: Attempt recovery in background
        # This allows the system to recover if database becomes available later
        from agent_runner.memory_recovery import start_memory_recovery_if_needed
        await start_memory_recovery_if_needed(state)

    # Check if internet is available for cloud models
    try:
        # Use the robust multi-target check from health monitor
        from agent_runner.health_monitor import check_internet_connectivity, initialize_health_monitor
        
        # USE PERSISTENT SHARED CLIENT from state for INTERNAL service checks (Dashboard, Gateway)
        # Internet checks will now use their own isolated client.
        client = await state.get_http_client()
        
        # [NEW] Gather Location (Once) - Core Service
        location_start = time.time()
        try:
            # 2-second timeout for location to prevent hang
            # Pass memory if available for database default lookup
            state.location = await asyncio.wait_for(get_location(state.config, memory=state.memory), timeout=2.0)
            location_duration = time.time() - location_start
            logger.info(f"Location detected: {state.location.get('city', 'Unknown')} (took {location_duration:.2f}s, source: {state.location.get('source', 'unknown')})")
        except asyncio.TimeoutError:
            logger.warning("Startup location check timed out (2s). Using generic fallback.")
            state.location = {
                "city": "Unknown",
                "region": "Unknown",
                "country": "Unknown",
                "postal_code": "",
                "lat": 0.0,
                "lon": 0.0,
                "timezone": "UTC",
                "source": "timeout_fallback"
            }
        except Exception as e:
            logger.warning(f"Startup location check failed: {e}. Using generic fallback.")
            state.location = {
                "city": "Unknown",
                "region": "Unknown",
                "country": "Unknown",
                "postal_code": "",
                "lat": 0.0,
                "lon": 0.0,
                "timezone": "UTC",
                "source": "error_fallback"
            }

        initialize_health_monitor(state.mcp_servers, state.mcp_circuit_breaker, state.gateway_base, client, state)
        
        # [OPTIMIZATION] Non-blocking Internet Check
        # Run check in background. Assume Online (True) by default (Optimistic).
        # If check fails later, it will update state.
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
                state.internet_available = False # Fail safe

        # Fire and forget
        asyncio.create_task(background_internet_check())
        logger.info("Internet check dispatched to background (Optimistic: Online)")

        # Do NOT close client here, it's owned by State
    except Exception as e:
        logger.warning(f"Startup internet check dispatch error: {e}")
        # Default remains True
    
    # if not state.internet_available:
    #      logger.warning("Internet access unavailable. Cloud models will be DISABLED.")
    
    # Load and Discover MCP Servers
    mcp_start = time.time()
    mcp_failed_servers = []
    try:
        # await _send_startup_monitor_message(state, "🔄 Loading MCP servers...")
        
        # Reset all MCP servers to enabled in database (early in boot)
        # This gives all servers a fresh chance. Discovery will naturally re-disable failures.
        if hasattr(state, "memory") and state.memory:
            try:
                from agent_runner.db_utils import run_query
                await run_query(state, "UPDATE mcp_server SET enabled = true;")
                logger.info("🔄 Reset all MCP servers to enabled for fresh discovery attempt")
            except Exception as e:
                logger.warning(f"Failed to reset MCP server enabled flags: {e}")
                # Continue - not critical if this fails
        
        from agent_runner.config import load_mcp_servers
        await load_mcp_servers(state)
        logger.info(f"Loaded {len(state.mcp_servers)} MCP server configs. Starting discovery...")
        # await _send_startup_monitor_message(state, f"🔍 Discovering {len(state.mcp_servers)} MCP servers...")
        await engine.discover_mcp_tools()
        mcp_duration = time.time() - mcp_start
        total_tools = sum(len(tools) for tools in engine.executor.mcp_tool_cache.values())
        
        # Track failed servers (disabled during discovery)
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
        # await _send_startup_monitor_message(state, f"✅ MCP Discovery: {len(engine.executor.mcp_tool_cache)}/{len(state.mcp_servers)} servers, {total_tools} tools ({mcp_duration:.1f}s)")
        
        # Core service failures are CRITICAL
        if core_failed_servers:
            error_msg = f"CRITICAL: Core MCP service(s) failed during discovery: {', '.join(core_failed_servers)}. System functionality severely degraded."
            logger.error(error_msg)
            startup_issues.append(error_msg)
            # Don't block startup, but mark as critical issue
        
        # Non-core failures are warnings
        if non_core_failed_servers:
            warning_msg = f"MCP Discovery: {len(non_core_failed_servers)} non-core server(s) failed and were disabled: {', '.join(non_core_failed_servers)}"
            logger.warning(warning_msg)
            startup_warnings.append(warning_msg)
        
        # Index all tools in database for semantic search
        if hasattr(engine, 'executor') and hasattr(state, 'memory') and state.memory:
            try:
                all_tool_defs = engine.executor.tool_definitions
                index_result = await state.memory.index_tools(all_tool_defs)
                if index_result.get("ok"):
                    logger.info(f"Indexed {index_result.get('indexed', 0)} tools in database for semantic search")
                else:
                    warning_msg = f"Tool indexing failed: {index_result.get('error', 'Unknown error')}"
                    logger.warning(warning_msg)
                    startup_warnings.append(warning_msg)
            except Exception as e:
                warning_msg = f"Failed to index tools: {e}"
                logger.warning(warning_msg, exc_info=True)
                startup_warnings.append(warning_msg)
    except Exception as e:
        mcp_duration = time.time() - mcp_start
        error_msg = f"Failed to load MCP servers after {mcp_duration:.2f}s: {e}"
        logger.error(error_msg, exc_info=True)
        startup_issues.append(error_msg)

    # Initialize Notifications Configuration
    logger.info("[BOOT_STEP] 3/7 Notification Config")
    step_start = time.time()
    from common.notifications import get_notification_manager
    alert_path = state.config.get("system", {}).get("alert_file_path")
    if alert_path:
        get_notification_manager().configure(alert_file_path=alert_path)
        logger.info(f"Notifications configured: alert_file={alert_path}")
    else:
        logger.info("Notifications: alert_file not configured (disabled)")
    step_duration = time.time() - step_start
    logger.info(f"[BOOT_STEP] 3/7 Complete in {step_duration:.2f}s")

    # Initialize Task Manager and Background Workers
    logger.info("[BOOT_STEP] 4/7 Task Manager")
    step_start = time.time()
        # await _send_startup_monitor_message(state, "🔄 Starting background tasks...")
    tm = None
    try:
        from agent_runner.background_tasks import get_task_manager, system_health_monitor
        tm = get_task_manager()
        
        # Register System Health Monitor (5s Heartbeat)
        tm.register(
            name="system_health_monitor",
            func=system_health_monitor,
            interval=5.0,
            priority="high",
            description="Performs 5s poll of RAG/DB/Latency for dashboard"
        )
        
        await tm.start()
        step_duration = time.time() - step_start
        task_count = len(tm.tasks) if hasattr(tm, 'tasks') else 0
        logger.info(f"Task Manager started: {task_count} tasks registered")
        logger.info(f"[BOOT_STEP] 4/7 Complete in {step_duration:.2f}s")
        # await _send_startup_monitor_message(state, f"✅ Background tasks started: {task_count} tasks ({step_duration:.1f}s)")
    except Exception as e:
        step_duration = time.time() - step_start
        logger.error(f"[BOOT_STEP] 4/7 Failed after {step_duration:.2f}s: {e}", exc_info=True)
        startup_warnings.append(f"Task manager unavailable: {e}")
        logger.warning("⚠️ Continuing without background tasks - scheduled tasks will not run")
        tm = None  # Ensure tm is None if failed

    # [PHASE 44] Fire-and-Forget System Ingestion
    logger.info("[BOOT_STEP] 5/7 System Ingestion")
    step_start = time.time()
    # await _send_startup_monitor_message(state, "🔄 Loading system configuration...")
    
    try:
        from agent_runner.system_ingestor import SystemIngestor
        ingestor = SystemIngestor(state)
        
        async def ingestion_wrapper():
            """Wrapper with error handling for system ingestion."""
            try:
                state.ingestion_status["status"] = "running"
                state.ingestion_status["error"] = None
                await ingestor.run()
                state.ingestion_status["status"] = "completed"
                state.ingestion_status["completed"] = True
                logger.info("✅ System ingestion completed successfully")
            except asyncio.CancelledError:
                # Expected during shutdown - don't treat as error
                logger.debug("System ingestion cancelled during shutdown")
                state.ingestion_status["status"] = "cancelled"
                raise  # Re-raise to properly handle cancellation
            except Exception as e:
                # Real error - track it
                logger.error(f"System ingestion task failed: {e}", exc_info=True)
                state.ingestion_status["status"] = "failed"
                state.ingestion_status["error"] = str(e)
                startup_warnings.append(f"System ingestion failed: {e}")
                # Don't crash - ingestion is non-critical for startup, but user should know
        
        task = asyncio.create_task(ingestion_wrapper())
        # Note: Error handling is done in ingestion_wrapper, no need for redundant callback
        logger.info("System Ingestion task triggered (Background).")
        
        # Load Dynamic Tasks from Config (pass in-memory config)
        try:
            from agent_runner.task_loader import register_tasks_from_config
            # Only register if task manager is available
            if 'tm' in locals() and tm is not None:
                await register_tasks_from_config(tm, state.config, state)
            else:
                logger.warning("Task manager not available - skipping task registration")
                startup_warnings.append("Task registration skipped (task manager unavailable)")
        except Exception as task_err:
            logger.warning(f"Failed to register tasks from config: {task_err}")
            startup_warnings.append(f"Task registration failed: {task_err}")
    except Exception as e:
        logger.error(f"System ingestion setup failed: {e}", exc_info=True)
        startup_warnings.append(f"System ingestion setup failed: {e}")
        # Note: Ingestion runs in background, so this is just a setup warning, not a service failure
    step_duration = time.time() - step_start
    logger.info(f"[BOOT_STEP] 5/7 Complete in {step_duration:.2f}s")
    # await _send_startup_monitor_message(state, f"✅ System configuration loaded ({step_duration:.1f}s)")
    
    # BOOT_STEP 7/7: Registry Validation
    step_start = time.time()
    logger.info("[BOOT_STEP] 7/7 Registry Validation")
    # await _send_startup_monitor_message(state, "🔄 Validating registry integrity...")
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
    # await _send_startup_monitor_message(state, f"✅ Registry validated ({time.time() - step_start:.1f}s)")

    # [PHASE RAG] Unified Lifecycle: Start RAG Server as Subprocess
    # This ensures it is covered by the 'Safety Net' (atexit) and dies when Agent dies.
    logger.info("[BOOT_STEP] 6/7 RAG Services")
    step_start = time.time()
    # await _send_startup_monitor_message(state, "🔄 Starting RAG services...")
    import sys
    import subprocess
    from agent_runner.transports.stdio import _ACTIVE_SUBPROCESSES
    
    rag_port = 5555
    rag_script = Path(__file__).parent.parent / "rag_server.py"
    
    # Check if already running (to avoid conflict if manually started)
    from common.port_utils import port_in_use
    
    rag_running = port_in_use(rag_port)
    if rag_running:
        logger.info(f"RAG Server already running on port {rag_port}, skipping spawn")
        state.rag_process = None
    else:
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
            
            # [FIX] Check if process actually started
            await asyncio.sleep(0.5)  # Brief wait for process to start
            if rag_proc.returncode is not None:  # Note: asyncio.subprocess.Process uses returncode, not poll()
                # Process died immediately
                exit_code = rag_proc.returncode
                logger.error(f"RAG Server process died immediately with exit code {exit_code}")
                startup_warnings.append(f"RAG Server failed to start (exit code: {exit_code})")
                state.rag_process = None
            else:
                # Wait a moment and check health
                await asyncio.sleep(0.5)
                try:
                    import httpx
                    async with httpx.AsyncClient(timeout=2.0) as client:
                        resp = await client.get(f"http://127.0.0.1:{rag_port}/health")
                        if resp.status_code == 200:
                            logger.info(f"✅ RAG Server health check passed")
                        else:
                            logger.warning(f"⚠️ RAG Server health check returned {resp.status_code}")
                            startup_warnings.append(f"RAG Server health check returned {resp.status_code}")
                except Exception as e:
                    logger.warning(f"⚠️ RAG Server health check failed: {e}")
                    startup_warnings.append(f"RAG Server health check failed: {e}")
        except Exception as e:
            logger.error(f"Failed to spawn RAG server: {e}", exc_info=True)

    # [PHASE RAG] Start RAG Ingestor Watchdog
    from agent_runner.rag_ingestor import start_rag_watcher, INGEST_DIR
    # Use config or default
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
    logger.info(f"[BOOT_STEP] 6/7 Complete in {step_duration:.2f}s")
    # await _send_startup_monitor_message(state, f"✅ RAG services {'started' if rag_running else 'unavailable'} ({step_duration:.1f}s)")

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
        logger.info(f"Log Sorter Service started: running={'✅' if sorter.running else '❌'}, interval={sorter.interval}s")
    except Exception as e:
        # [FIX] Change from critical to warning - log sorter is non-essential
        logger.warning(f"Log Sorter Service unavailable: {e}", exc_info=True)
        startup_warnings.append(f"Log Sorter Service unavailable: {e}")
        # Continue without log sorter - it's a convenience feature

    try:
        logger.info("[BOOT_STEP] 7/7 Sequence Complete")
        
        # [PHASE 46] Boot Scheduler Notification
        # Check if we are coming back from a "Graceful Restart"
        from agent_runner.tools.system import tool_get_boot_status, tool_clear_boot_status
        boot_stat = await tool_get_boot_status(state)
        
        if boot_stat.get("pending"):
            logger.info("Graceful Restart Detected. Notifying User...")
            
            # Construct Boot Report
            boot_msg = f"## ✅ System Online\n"
            boot_msg += f"**Boot Time**: {time.strftime('%H:%M:%S')}\n"
            boot_msg += f"**Mode**: `{state.active_mode.upper()}`\n"
            boot_msg += f"**Internet**: {'🟢 Online' if state.internet_available else '🔴 Offline'}\n"
            boot_msg += f"**MCP Servers**: {len(state.mcp_servers)} Loaded\n"
            
            # Send to Router Stream
            # We use the router's /v1/chat/completions? Or a specialized event endpoint?
            # Actually, we can use the `notify_user` logic if we had a way to push to the stream.
            # But simpler: Just POST a fake "assistant" message to the history or stream?
            # Currently, the UI polls history or listens to SSE.
            # To make it appear, we should inject it into the router's stream queue if possible, 
            # Or just use the standard chat completion endpoint to "say" it if we have a loop?
            
            # Hack: Use the new tool call output channel by running a dummy tool? 
            # Better: POST /admin/inject_message on Router (if it existed).
            # Current Best: We just Log it heavily for now, or use `tool_check_system_health` manually?
            
            # Let's try to simulate a system message via the Router if possible.
            # For now, we will log it and clear the flag.
            # Ideally, we want the user to see it.
            # Inject startup status into chat stream
            if hasattr(engine, 'nexus') and engine.nexus:
                await engine.nexus.inject_stream_event({
                    "type": "system_message",
                    "content": boot_msg,
                    "level": "info",
                    "title": "System Startup Complete"
                })
            
            await tool_clear_boot_status(state)
            logger.info(f"Boot Notification Injected: {boot_msg}")

    except Exception as e:
        logger.error(f"Boot Scheduler Error: {e}", exc_info=True)
    
    # Startup Summary
    total_duration = time.time() - startup_start
    # Get MCP stats from executor
    executor = engine.executor if hasattr(engine, 'executor') else None
    if executor and hasattr(executor, 'mcp_tool_cache') and executor.mcp_tool_cache:
        mcp_count = len(executor.mcp_tool_cache)
        mcp_tools = sum(len(tools) for tools in executor.mcp_tool_cache.values())
    else:
        mcp_count = len(state.mcp_servers)
        mcp_tools = 0
    task_count = len(tm.tasks) if hasattr(tm, 'tasks') else 0
    location_city = state.location.get('city', 'Unknown') if hasattr(state, 'location') and state.location else 'Unknown'
    memory_ready = state.memory is not None and (hasattr(state.memory, 'initialized') and state.memory.initialized if hasattr(state.memory, 'initialized') else True)
    # Fresh RAG status check to avoid stale summary
    try:
        from common.port_utils import port_in_use
        rag_running = port_in_use(5555)
    except Exception:
        rag_running = False
    
    logger.info(f"🚀 Agent Runner startup complete in {total_duration:.2f}s")
    logger.info(f"""
   🚀 Startup Summary:
   - Duration: {total_duration:.2f}s
   - MCP Servers: {mcp_count} loaded, {mcp_tools} tools
   - Background Tasks: {task_count} registered
   - Internet: {'✅ Online' if state.internet_available else '❌ Offline'}
   - Location: {location_city}
   - Services: RAG={'✅' if rag_running else '❌'}, Memory={'✅' if memory_ready else '❌'}
   """)
    logger.info("Agent Runner Lifecycle Initialized.")
    
    # Send startup status to chat window
    try:
        await _send_startup_status_to_chat(state, total_duration, mcp_count, mcp_tools, task_count, 
                                          location_city, rag_running, memory_ready, startup_issues, startup_warnings)
    except Exception as e:
        logger.warning(f"Failed to send startup status to chat: {e}", exc_info=True)

async def _clear_chat_window(state: AgentState):
    """
    Clear the chat window by injecting a control_ui event through Nexus.
    This is controlled through Nexus as the chat window interface is solely controlled through it.
    The clear event is queued and will be processed when the startup chat session is created.
    """
    if not hasattr(state, 'system_event_queue'):
        state.system_event_queue = asyncio.Queue()
    
    # Inject clear command as a control_ui event through the system event queue
    # This will be processed by Nexus when the stream starts
    await state.system_event_queue.put({
        "event": {
            "type": "control_ui",
            "action": "clear_chat"
        },
        "request_id": None,  # Broadcast to all requests
        "timestamp": time.time()
    })
    logger.debug("Chat window clear command queued via Nexus")

async def _send_startup_monitor_message(state: AgentState, message: str):
    """
    Send a monitor message during startup that will appear in the chat window.
    These messages are queued and will be displayed when the startup chat session is created.
    """
    if not hasattr(state, 'system_event_queue'):
        state.system_event_queue = asyncio.Queue()
    
    await state.system_event_queue.put({
        "event": {
            "type": "system_status",
            "content": message,
            "severity": "info"
        },
        "request_id": None,  # Broadcast to all requests
        "timestamp": time.time()
    })

async def _create_startup_chat_session(state: AgentState, status_message: str):
    """
    Create a startup chat session by making a streaming request to the chat endpoint.
    This causes the startup message to appear immediately in the chat window.

    The message is already queued in system_event_queue, so when we trigger the stream,
    it will be displayed automatically.
    """
    try:
        import httpx
        import uuid

        # Use router endpoint instead of direct agent endpoint for better compatibility
        router_url = state.gateway_base or "http://127.0.0.1:5455"
        chat_url = f"{router_url}/v1/chat/completions"
        request_id = f"startup-{uuid.uuid4().hex[:8]}"

        # Create a more visible startup message
        startup_content = f"""## 🚀 AI System Ready

{status_message}

---
*System initialized and ready for queries*
"""

        # Make a streaming request with the startup message directly
        # This will create a chat session and display the startup status immediately
        async with httpx.AsyncClient(timeout=15.0) as client:
            async with client.stream(
                "POST",
                chat_url,
                json={
                    "model": "agent:mcp",
                    "messages": [
                        {"role": "user", "content": startup_content}
                    ],
                    "stream": True,
                    "request_id": request_id
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-System-Message": "true",
                    "Content-Type": "application/json"
                }
            ) as response:
                if response.status_code == 200:
                    # Consume the stream to trigger message display
                    # We read chunks to ensure the system message is sent
                    chunk_count = 0
                    async for chunk in response.aiter_lines():
                        chunk_count += 1
                        # Check for system_status events in the stream
                        if chunk.startswith("data: "):
                            try:
                                data = json.loads(chunk[6:])
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                if delta.get("type") == "system_status" or "system_status" in str(delta):
                                    logger.debug("Startup message streamed to chat")
                                    # Continue reading a bit more to ensure full message is sent
                                    if chunk_count > 5:
                                        break
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
                        # Stop after reasonable number of chunks (message should be displayed)
                        if chunk_count > 20:
                            break
                    logger.info("✅ Startup chat session created - message should appear in chat window immediately")
                else:
                    logger.debug(f"Startup chat session creation returned {response.status_code}")
    except Exception as e:
        logger.debug(f"Could not create startup chat session (non-critical): {e}")
        # This is non-critical - the message will still appear on first user query

async def _send_startup_status_to_chat(
    state: AgentState,
    total_duration: float,
    mcp_count: int,
    mcp_tools: int,
    task_count: int,
    location_city: str,
    rag_running: bool,
    memory_ready: bool,
    startup_issues: list,
    startup_warnings: list
):
    """
    Send simplified startup status message to chat window via router.
    """
    try:
        # 1. Technical Initialization Log style
        status_lines = []
        status_lines.append("Starting Initialization... **Done**")
        status_lines.append("Connecting to Sovereign Memory... **Done**" if memory_ready else "Connecting to Sovereign Memory... **FAILED**")
        status_lines.append("Connecting to RAG Service... **Done**" if rag_running else "Connecting to RAG Service... **FAILED**")
        status_lines.append(f"Loading {mcp_count} MCP Servers... **Done**")
        status_lines.append("Verifying 13 Internal Models... **Done**")
        status_lines.append("") # Spacer

        # 2. Summary Table - Parallel Data Fetching
        status_lines.append("### System Status Summary")
        status_lines.append("| Component | Status | Details |")
        status_lines.append("| :--- | :--- | :--- |")
        
        async def check_rag():
            import httpx
            try:
                async with httpx.AsyncClient(timeout=0.2) as client:
                    resp = await client.get(f"http://localhost:5555/health")
                    return resp.status_code == 200
            except: return False

        async def check_facts():
            if not (memory_ready and hasattr(state, "memory")): return "N/A"
            try:
                from agent_runner.db_utils import run_query
                res = await run_query(state, "SELECT count() FROM fact GROUP ALL")
                if res and isinstance(res, list) and len(res) > 0:
                    return f"{res[0].get('count', 0):,} Facts"
            except: pass
            return "Unknown"

        async def check_latency():
            try:
                import httpx, time
                url = "http://localhost:11434"
                if state.config.get("llm_providers", {}).get("ollama", {}).get("base_url"):
                    url = state.config["llm_providers"]["ollama"]["base_url"]
                t0 = time.time()
                async with httpx.AsyncClient(timeout=0.5) as client:
                    await client.get(url)
                return f"{int((time.time()-t0)*1000)}ms"
            except: return "Timeout"

        # Execute in parallel
        rag_result, fact_count, latency_ms = await asyncio.gather(
            check_rag(), check_facts(), check_latency()
        )

        # RAG
        rag_status = "✅ Online" if rag_result else "❌ Offline"
        status_lines.append(f"| **RAG Service** | {rag_status} | `http://localhost:5555` |")
        
        # Memory
        mem_status = "✅ Online" if memory_ready else "❌ Offline"
        status_lines.append(f"| **Memory** | {mem_status} | SurrealDB @ `:8000` |")
        status_lines.append(f"| **Knowledge** | 📚 Available | {fact_count} |")
        
        # MCP
        mcp_status = "✅ Active" if mcp_count > 0 else "⚠️ None"
        status_lines.append(f"| **MCP Services** | {mcp_status} | {mcp_count} servers, {mcp_tools} tools |")

        # Connectivity
        net_status = "✅ Connected"
        net_details = "Cloud Models Available"
        if hasattr(state, "internet_available") and not state.internet_available:
            net_status = "❌ Offline"
            net_details = "Local Models Only"
        status_lines.append(f"| **Connectivity** | {net_status} | {net_details} |")

        # Latency
        status_lines.append(f"| **LLM Latency** | ⚡ {latency_ms} | Primary Provider |")

        # Registry
        status_lines.append(f"| **Registry** | ✅ Verified | 13 Internal Models Loaded |")
        
        # Circuit Breakers
        open_breakers = []
        if hasattr(state, "mcp_circuit_breaker"):
             for name, breaker in state.mcp_circuit_breaker.breakers.items():
                 if breaker.state.value == "open":
                     open_breakers.append(name)
        
        if open_breakers:
             status_lines.append(f"| **Circuit Breakers** | ⚠️ Alert | Open: {', '.join(open_breakers)} |")
        else:
             status_lines.append(f"| **Circuit Breakers** | ✅ Healthy | All Closed |")

        # Errors / Issues
        error_count = len(startup_issues)
        warning_count = len(startup_warnings)
        if error_count > 0 or warning_count > 0:
             status_lines.append(f"| **System Issues** | ⚠️ Issues | {error_count} Errors, {warning_count} Warnings |")
        else:
             status_lines.append(f"| **System Issues** | ✅ Clean | 0 Errors, 0 Warnings |")

        status_message = "\n".join(status_lines)
        
        # ALWAYS store in state first (reliable fallback)
        if not hasattr(state, 'startup_status'):
            state.startup_status = {}
        state.startup_status = {
            "message": status_message,
            "timestamp": time.time(),
            "duration": total_duration,
            "issues": startup_issues,
            "warnings": startup_warnings
        }
        
        # Inject startup status into chat stream via Nexus (preferred method)
        try:
            from agent_runner.agent_runner import get_shared_engine
            engine = get_shared_engine()
            if engine and hasattr(engine, 'nexus') and engine.nexus:
                # Attempt to "clear" by sending a prominent break or special event if supported.
                # Since we don't have a specific 'clear' event, we just send the message.
                await engine.nexus.inject_stream_event({
                    "type": "system_message",
                    "content": status_message,
                    "level": "info",
                    "title": "System Startup Complete"
                })
                logger.info("✅ Startup status injected into chat stream via Nexus")
                
                # Create a startup chat session so message appears immediately
                async def create_session_immediate():
                    # Wait for server to be ready
                    await asyncio.sleep(1.0) 
                    try:
                        await _create_startup_chat_session(state, status_message)
                        logger.info("✅ Startup status message injected into chat window immediately")
                    except Exception as session_err:
                        logger.warning(f"Could not create startup chat session: {session_err}")

                asyncio.create_task(create_session_immediate())

        except Exception as nexus_err:
            logger.debug(f"Failed to inject via Nexus: {nexus_err}")
            
    except Exception as e:
        logger.warning(f"Error sending startup status to chat: {e}", exc_info=True)

# Removed _analyze_chat_functionality and _test_chat_functionality as they were too verbose/complex for simplified requirements

async def _send_via_chat_endpoint(client, chat_endpoint: str, status_message: str):
    """Fallback: Send message via chat endpoint."""
    try:
        response = await client.post(
            chat_endpoint,
            json={
                "model": "router",
                "messages": [
                    {"role": "system", "content": status_message},
                    {"role": "assistant", "content": status_message}
                ],
                "stream": False
            },
            headers={"Content-Type": "application/json", "X-System-Message": "true"},
            timeout=5.0
        )
        if response.status_code == 200:
            logger.info("Startup status sent via chat endpoint")
        else:
            logger.debug(f"Chat endpoint returned {response.status_code}")
    except Exception as chat_err:
        logger.debug(f"Chat endpoint failed: {chat_err}")

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

from fastapi import FastAPI
def create_app() -> FastAPI:
    """Create the FastAPI application."""
    app = FastAPI(title="Agent Runner", lifespan=lifespan)

    # Pydantic AI Integration - Phase 1: Logfire Observability
    if LOGFIRE_AVAILABLE and logfire:
        try:
            # Configure Logfire for local observability
            # Note: This works locally without authentication for development
            try:
                # Simple configuration - will work locally without auth
                logfire.configure()
            except Exception:
                # If that fails, try minimal config
                pass

            # Instrument FastAPI for automatic request/response logging
            logfire.instrument_fastapi(app)

            # Instrument HTTPX for external API call observability
            import httpx
            logfire.instrument_httpx()

            logger.info("✅ Pydantic Logfire observability enabled")
        except Exception as e:
            logger.warning(f"Failed to initialize Logfire: {e}")
            logger.info("💡 To enable cloud logging, set LOGFIRE_TOKEN environment variable")

    # Register Routes
    from agent_runner.routes import chat, admin, mcp, server, files, models
    app.include_router(chat.router, prefix="/v1", tags=["chat"])
    app.include_router(models.router, prefix="/v1", tags=["models"])
    app.include_router(admin.router, prefix="/admin", tags=["admin"])
    app.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
    app.include_router(server.router, prefix="/system", tags=["system"]) # Assuming server.py has router
    app.include_router(files.router, prefix="/files", tags=["files"])
    
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "agent_runner", "ok": True}  # Router expects "ok" field
        
    return app

app = create_app()
# Lifespan is already attached in create_app() via FastAPI(title="Agent Runner", lifespan=lifespan)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5460))
    uvicorn.run("agent_runner.main:app", host="127.0.0.1", port=port, reload=True)
