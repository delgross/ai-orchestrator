import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from common.logging_setup import setup_logger
from common.unified_tracking import track_event, EventCategory, EventSeverity

from router.config import state, VERSION, OLLAMA_BASE, AGENT_RUNNER_URL, RAG_BASE
from router.providers import load_providers
from router.app import create_app
from router.utils import log_time
from common.observability import get_observability
from common.anomaly_detection_task import run_anomaly_detection
from router.routes.config import get_config # Re-use the fetcher logic

logger = setup_logger("router")

# [DEBUG] Log auth token configuration at startup
import sys
from router import config
logger.info(f"🔐 ROUTER_AUTH_TOKEN loaded: {'<set>' if config.ROUTER_AUTH_TOKEN else '<EMPTY>'} (len={len(config.ROUTER_AUTH_TOKEN)})")
if not config.ROUTER_AUTH_TOKEN:
    logger.warning("⚠️ Authentication DISABLED - ROUTER_AUTH_TOKEN is empty!")
    pytest_modules = [m for m in sys.modules if 'pytest' in m.lower()]
    if pytest_modules:
        logger.warning(f"⚠️ Pytest modules detected (may have disabled auth): {pytest_modules[:5]}")

async def run_config_sync():
    """Periodically sync system config from DB."""
    logger.info("🔄 Starting Config Sync Task...")
    while True:
        try:
            # Sync Router Mode
            res = await get_config("router_mode")
            val = res.get("value")
            if val and val in ["sync", "async"]:
                if state.router_mode != val:
                    logger.info(f"Config Sync: Switched router_mode to '{val}'")
                    state.router_mode = val
        except Exception as e:
            logger.debug(f"Config Sync failed (transient): {e}")
        
        await asyncio.sleep(5)


async def run_api_key_sync_loop():
    """Periodically refresh API keys from DB."""
    logger.info("🔑 Starting API Key Sync Task...")
    while True:
        try:
           for p in state.providers.values():
               await p.load_api_key(state.client)
        except Exception as e:
            logger.debug(f"API Key Sync failed: {e}")
        await asyncio.sleep(60)

async def run_environment_watchdog():
    """Continuously check critical dependencies."""
    from router.health_check_helpers import check_service_health
    
    logger.info("🛡️ Starting Environment Watchdog...")
    
    while True:
        try:
            # 1. Check Ollama
            await check_service_health("ollama", f"{OLLAMA_BASE}/api/tags", state.circuit_breakers, state.client)

            # 2. Check Agent Runner
            await check_service_health("agent_runner", f"{AGENT_RUNNER_URL}/health", state.circuit_breakers, state.client)

            # 3. Check RAG Server
            await check_service_health("rag_server", f"{RAG_BASE}/health", state.circuit_breakers, state.client)

            # 4. DEADLOCK CHECK
            # If both Ollama and Agent Runner are broken, we might be in a deadlock 
            # (Router waiting for Agent which waits for Ollama which waits for Router...)
            criticals = ["ollama", "agent_runner"]
            if state.circuit_breakers.detect_system_lockdown(criticals):
                logger.critical("DEADLOCK DETECTED! Both Ollama and Agent Runner are tripping.")
                state.circuit_breakers.emergency_release_lockdown(criticals)
                # Optional: Send a specific notification here if desired

        except Exception as e:
            logger.error(f"Watchdog crash: {e}")
        
        await asyncio.sleep(60) 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting Router v{VERSION}")
    track_event("router_startup", severity=EventSeverity.INFO, category=EventCategory.SYSTEM, message=f"Router version {VERSION} starting up")
    setup_logger("common.circuit_breaker", log_file="router.log")

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

    # [NEW] Router Startup Validation
    logger.info("🔍 Validating router startup...")
    router_errors = []
    router_warnings = []

    # Validate cache freshness
    try:
        from router.health_check_helpers import check_cache_freshness
        is_cache_fresh, stale_files = check_cache_freshness()
        if not is_cache_fresh:
            router_warnings.append(f"Stale bytecode detected: {len(stale_files)} files")
            logger.warning(f"⚠️ Router startup found {len(stale_files)} stale bytecode files")
        else:
            logger.info("✅ Bytecode cache is fresh")
    except Exception as e:
        router_warnings.append(f"Cache check failed: {e}")
        logger.warning(f"⚠️ Cache freshness check failed: {e}")

    # Validate critical imports
    try:
        from common.logging_utils import log_time
        from router.routes.chat import chat_completions
        from router.routes.embeddings import embeddings
        logger.info("✅ All router imports validated")
    except ImportError as e:
        router_errors.append(f"Missing import: {e}")
        logger.error(f"❌ Router import validation failed: {e}")
    except Exception as e:
        router_warnings.append(f"Import validation warning: {e}")
        logger.warning(f"⚠️ Router import validation warning: {e}")

    # Validate route handlers exist
    try:
        from router.routes.chat import _dispatch_chat
        from router.providers import call_ollama_chat
        logger.info("✅ All route handlers validated")
    except (ImportError, AttributeError) as e:
        router_errors.append(f"Route handler validation failed: {e}")
        logger.error(f"❌ Route handler validation failed: {e}")
    
    if router_errors:
        logger.error(f"Router startup validation failed with {len(router_errors)} errors")
        # Don't crash - mark as degraded
        state.router_degraded = True
        state.router_errors = router_errors
    
    if router_warnings:
        logger.warning(f"Router startup validation found {len(router_warnings)} warnings")
        if not hasattr(state, 'router_warnings'):
            state.router_warnings = []
        state.router_warnings.extend(router_warnings)
    
    state.providers = load_providers()
    logger.warning(f"🚀 ROUTER STARTUP: Loaded {len(state.providers)} providers: {list(state.providers.keys())}")
    
    # [NEW] Initial API Key Load
    logger.info("🔑 performing initial API key load...")
    for p in state.providers.values():
        await p.load_api_key(state.client)

    # Start Background Tasks
    try:
        env_task = asyncio.create_task(run_environment_watchdog())
        anomaly_task = asyncio.create_task(run_anomaly_detection(check_interval=60.0))
        conf_task = asyncio.create_task(run_config_sync())
        key_task = asyncio.create_task(run_api_key_sync_loop())
    except Exception as e:
        logger.warning(f"Failed to start some background tasks: {e}")
        # Continue - background tasks are non-critical
    
    yield
    # Shutdown
    track_event("router_shutdown", severity=EventSeverity.INFO, category=EventCategory.SYSTEM, message="Router is shutting down")
    
    env_task.cancel()
    anomaly_task.cancel()
    conf_task.cancel()
    key_task.cancel()
    try:
        await env_task
        await anomaly_task
        await conf_task
        await key_task
    except asyncio.CancelledError:
        pass
    await state.client.aclose()
    
    obs = get_observability()

# Create the application instance
app = create_app(lifespan=lifespan)
