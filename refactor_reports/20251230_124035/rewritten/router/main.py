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
                r = await state.client.get(f"{OLLAMA_BASE}/api/tags", timeout=1.0)
                if r.status_code != 200:
                    logger.warning(f"⚠️ Watchdog: Ollama returned {r.status_code}")
            except Exception as e:
                logger.error(f"❌ Watchdog: Ollama is OFFLINE: {e}")

            # 2. Check Agent Runner
            try:
                r = await state.client.get(f"{AGENT_RUNNER_URL}/health", timeout=1.0)
                if r.status_code != 200:
                    logger.warning(f"⚠️ Watchdog: Agent Runner returned {r.status_code}")
            except Exception:
                pass 

            # 3. Check RAG Server
            try:
                r = await state.client.get(f"{RAG_BASE}/health", timeout=1.0)
                if r.status_code != 200:
                    logger.warning(f"⚠️ Watchdog: RAG Server returned {r.status_code}")
            except Exception as e:
                logger.error(f"❌ Watchdog: RAG Server is OFFLINE: {e}")

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
