import asyncio
import logging
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

logger = setup_logger("router")

async def run_environment_watchdog():
    """Continuously check critical dependencies."""
    logger.info("🛡️ Starting Environment Watchdog...")
    
    while True:
        try:
            # 1. Check Ollama
            try:
                # Check if breaker allows (fail fast)
                if state.circuit_breakers.is_allowed("ollama"):
                    r = await state.client.get(f"{OLLAMA_BASE}/api/tags", timeout=2.0)
                    if r.status_code == 200:
                        state.circuit_breakers.record_success("ollama")
                    else:
                        state.circuit_breakers.record_failure("ollama", error=f"HTTP {r.status_code}")
                # If NOT allowed, we skip the check to respect the timeout, but we don't record failure (it's open)
            except Exception as e:
                state.circuit_breakers.record_failure("ollama", error=str(e))
                logger.debug(f"Watchdog: Ollama check failed: {e}")

            # 2. Check Agent Runner
            try:
                if state.circuit_breakers.is_allowed("agent_runner"):
                    r = await state.client.get(f"{AGENT_RUNNER_URL}/health", timeout=2.0)
                    if r.status_code == 200:
                        state.circuit_breakers.record_success("agent_runner")
                    else:
                        state.circuit_breakers.record_failure("agent_runner", error=f"HTTP {r.status_code}")
            except Exception as e:
                state.circuit_breakers.record_failure("agent_runner", error=str(e))

            # 3. Check RAG Server
            try:
                if state.circuit_breakers.is_allowed("rag_server"):
                    r = await state.client.get(f"{RAG_BASE}/health", timeout=2.0)
                    if r.status_code == 200:
                        state.circuit_breakers.record_success("rag_server")
                    else:
                        state.circuit_breakers.record_failure("rag_server", error=f"HTTP {r.status_code}")
            except Exception as e:
                state.circuit_breakers.record_failure("rag_server", error=str(e))

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
    state.providers = load_providers()
    
    # Start Background Tasks
    env_task = asyncio.create_task(run_environment_watchdog())
    anomaly_task = asyncio.create_task(run_anomaly_detection(check_interval=60.0))
    
    yield
    # Shutdown
    track_event("router_shutdown", severity=EventSeverity.INFO, category=EventCategory.SYSTEM, message="Router is shutting down")
    
    env_task.cancel()
    anomaly_task.cancel()
    try:
        await env_task
        await anomaly_task
    except asyncio.CancelledError:
        pass
    await state.client.aclose()
    
    obs = get_observability()

# Create the application instance
app = create_app(lifespan=lifespan)
