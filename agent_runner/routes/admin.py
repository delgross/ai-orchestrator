import logging
import time
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, Body, Request, HTTPException
from pathlib import Path

from agent_runner.agent_runner import get_shared_state, get_shared_engine
from agent_runner.background_tasks import get_task_manager
from common.observability import get_observability

router = APIRouter()
logger = logging.getLogger("agent_runner.admin")

@router.get("/health")
async def health_check():
    state = get_shared_state()
    return {
        "status": "healthy",
        "ok": True,
        "internet": state.internet_available,
        "uptime_s": time.time() - state.started_at
    }

@router.get("/admin/health/detailed")
async def health_check_detailed():
    """Return a comprehensive health report including topology."""
    from agent_runner.health_monitor import get_detailed_health_report
    return await get_detailed_health_report()

@router.get("/metrics")
async def metrics():
    state = get_shared_state()
    obs = get_observability()
    
    # Legacy State Metrics
    avg_latency = 0
    if state.request_count > 0:
        avg_latency = state.total_response_time_ms / state.request_count
        
    # Automated Observability Metrics
    system_metrics = await obs.get_system_metrics()
    
    return {
        "ok": True,
        "requests": state.request_count,
        "errors": state.error_count,
        "avg_latency_ms": round(avg_latency, 2),
        "last_error": state.last_error,
        "observability": {
            "active_requests": system_metrics.active_requests,
            "requests_1min": system_metrics.completed_requests_1min,
            "avg_latency_1min_ms": round(system_metrics.avg_response_time_1min, 2),
            "error_rate_1min": round(system_metrics.error_rate_1min * 100, 2),
            "resource_usage": system_metrics.resource_usage,
            "efficiency": {
                "rps": round(system_metrics.efficiency.requests_per_second, 2),
                "cache_hit_rate": round(system_metrics.efficiency.cache_hit_rate, 2),
                "avg_wait_ms": round(system_metrics.efficiency.semaphore_wait_time_avg_ms, 2)
            }
        }
    }

@router.get("/admin/system-status")
async def system_status():
    state = get_shared_state()
    
    # 1. Real Service Checks (No Mocking)
    import aiohttp
    
    async def _check_url(url: str, timeout=0.5) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as resp:
                    return resp.status < 500
        except:
            return False

    # Check Ollama (Port 11434)
    ollama_ok = await _check_url("http://localhost:11434")
    
    # Check Database (SurrealDB Port 8000)
    # Surreal's health endpoint is /health or /status usually, or just root
    db_ok = await _check_url("http://localhost:8000/health") 
    
    # Internet is updated by background task, which is acceptable cache
    internet_status = "Connected" if state.internet_available else "Offline"
    
    return {
        "ok": True,
        "mode": state.system_mode,
        "internet": internet_status,
        "hardware_verified": state.hardware_verified,
        "cpu_usage": "Low", # Still simplified (requires psutil)
        "memory_info": "Optimal",
        "ollama_ok": ollama_ok,
        "database_ok": db_ok, # Explicitly returning DB status now
        "limits": {
            "max_read": state.max_read_bytes,
            "max_list": state.max_list_entries
        }
    }

@router.post("/admin/config/models")
async def update_models(config: Dict[str, str] = Body(...)):
    """Update system models dynamically."""
    state = get_shared_state()
    if "summarization_model" in config: state.summarization_model = config["summarization_model"]
    if "agent_model" in config: state.agent_model = config["agent_model"]
    if "task_model" in config: state.task_model = config["task_model"]
    if "router_model" in config: state.router_model = config["router_model"]

    save_system_config(state)
    return {
        "ok": True, 
        "models": {
            "summarization_model": state.summarization_model,
            "agent_model": state.agent_model,
            "task_model": state.task_model,
            "router_model": state.router_model
        }
    }

def save_system_config(state):
    """Save current state to system_config.json for persistence."""
    try:
        config_path = Path(__file__).parent.parent.parent / "system_config.json"
        
        # Load existing to avoid overwriting unrelated settings
        cfg = {}
        if config_path.exists():
            with open(config_path, "r") as f:
                cfg = json.load(f)
        
        cfg.update({
            "agent_model": state.agent_model,
            "summarization_model": state.summarization_model,
            "task_model": state.task_model,
            "router_model": state.router_model,
            "mcp_model": state.mcp_model,
            "finalizer_model": state.finalizer_model,
            "embedding_model": state.embedding_model,
            "vision_model": state.vision_model
        })

        with open(config_path, "w") as f:
            json.dump(cfg, f, indent=4)
        logger.info(f"Saved system configuration to {config_path}")
    except Exception as e:
        logger.error(f"Failed to save system_config.json: {e}")

@router.post("/admin/tasks/consolidation")
async def trigger_consolidation():
    """Manually trigger memory consolidation."""
    state = get_shared_state()
    from agent_runner.memory_tasks import memory_consolidation_task
    asyncio.create_task(memory_consolidation_task(state))
    return {"ok": True, "message": "Memory consolidation triggered in background"}

@router.post("/admin/tasks/backup")
async def trigger_backup():
    """Manually trigger memory backup."""
    # We use the shell script via manage.sh wrapper or direct execution
    # Ideally, we should wrap this in a python task, but for now spawning the script is fine
    import asyncio
    from agent_runner.config import PROJECT_ROOT
    
    script_path = f"{PROJECT_ROOT}/bin/backup_memory.sh"
    
    async def run_backup():
        try:
            logger.info("Starting background backup...")
            proc = await asyncio.create_subprocess_exec(
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                logger.info("Backup completed successfully.")
            else:
                logger.error(f"Backup failed: {stderr.decode()}")
        except Exception as e:
            logger.error(f"Backup task exception: {e}")

    # Fire and forget
    asyncio.create_task(run_backup())
    
    return {"ok": True, "message": "Backup triggered in background"}

@router.get("/admin/circuit-breaker/status")
async def circuit_breaker_status():
    state = get_shared_state()
    return {
        "ok": True,
        "breakers": state.mcp_circuit_breaker.get_status()
    }

@router.post("/admin/circuit-breaker/reset/{name}")
async def reset_circuit_breaker(name: str):
    state = get_shared_state()
    state.mcp_circuit_breaker.reset(name)
    return {"ok": True, "message": f"Circuit breaker '{name}' reset"}

@router.post("/admin/circuit-breaker/reset-all")
async def reset_all_circuit_breakers():
    state = get_shared_state()
    state.mcp_circuit_breaker.reset_all()
    return {"ok": True, "message": "All circuit breakers reset"}

@router.post("/admin/telemetry/log")
async def log_telemetry(request: Request):
    """Receive logs/errors from the frontend dashboard."""
    try:
        data = await request.json()
        level = data.get("level", "info").upper()
        msg = data.get("message", "No message")
        ctx = data.get("context", {})
        
        # Determine prefix for visibility
        prefix = f"[DASHBOARD-{level}]" 
        log_msg = f"{prefix} {msg} | {json.dumps(ctx) if ctx else ''}"
        
        if level == "ERROR":
            logger.error(log_msg)
        elif level == "WARN":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to process telemetry: {e}")
        return {"ok": False}

@router.get("/admin/background-tasks")
async def list_tasks():
    status = get_task_manager().get_status()
    return {
        "ok": True,
        "tasks": list(status["tasks"].values()),
        "meta": {
            "running": status["running"],
            "count": len(status["tasks"])
        }
    }

@router.get("/admin/system-prompt")
async def get_system_prompt():
    engine = get_shared_engine()
    prompt = await engine.get_system_prompt()
    return {"ok": True, "prompt": prompt}

@router.get("/admin/memory/facts")
async def get_memory_facts(query: str = "", limit: int = 100):
    state = get_shared_state()
    from agent_runner.tools.mcp import tool_mcp_proxy
    if query:
        res = await tool_mcp_proxy(state, "project-memory", "semantic_search", {"query": query, "limit": limit})
    else:
        res = await tool_mcp_proxy(state, "project-memory", "get_memory_stats", {})
    return res

@router.get("/admin/dashboard/insights")
async def get_dashboard_insights():
    state = get_shared_state()
    # Logic moved to dashboard_tracker potentially, but for now matching main.py
    # (Assuming it was a simple passthrough or mock)
    return {"ok": True, "insights": []}

@router.post("/admin/dashboard/errors")
async def track_dashboard_error(body: Dict[str, Any]):
    from agent_runner.dashboard_tracker import get_dashboard_tracker
    tracker = get_dashboard_tracker()
    tracker.record_error(**body)
    return {"ok": True}

@router.post("/admin/dashboard/interactions")
async def track_dashboard_interaction(body: Dict[str, Any]):
    from agent_runner.dashboard_tracker import get_dashboard_tracker
    tracker = get_dashboard_tracker()
    tracker.record_interaction(**body)
    return {"ok": True}

@router.get("/admin/system/logs")
async def get_logs_tail(lines: int = 100):
    """Return the last N lines of the agent runner log."""
    log_file = "agent_runner.log"
    if not Path(log_file).exists():
        return {"ok": False, "error": "Log file not found"}
    
    try:
        import subprocess
        res = subprocess.check_output(["tail", "-n", str(lines), log_file]).decode("utf-8")
        return {"ok": True, "logs": res}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/admin/llm/roles")
async def get_llm_roles():
    state = get_shared_state()
    return {
        "ok": True,
        "roles": {
            "agent_model": state.agent_model,
            "task_model": state.task_model,
            "summarization_model": state.summarization_model,
            "router_model": state.router_model,
            "mcp_model": state.mcp_model,
            "finalizer_model": state.finalizer_model,
            "embedding_model": state.embedding_model,
            "vision_model": state.vision_model
        }
    }

@router.post("/admin/llm/roles")
async def update_llm_roles(request: Request):
    state = get_shared_state()
    try:
        data = await request.json()
        if "agent_model" in data: state.agent_model = data["agent_model"]
        if "task_model" in data: state.task_model = data["task_model"]
        if "summarization_model" in data: state.summarization_model = data["summarization_model"]
        if "router_model" in data: state.router_model = data["router_model"]
        if "mcp_model" in data: state.mcp_model = data["mcp_model"]
        if "finalizer_model" in data: state.finalizer_model = data["finalizer_model"]
        if "embedding_model" in data: state.embedding_model = data["embedding_model"]
        if "vision_model" in data: state.vision_model = data["vision_model"]
        
        save_system_config(state)
        return {"ok": True, "message": "Roles updated successfully"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/admin/system/process/stop")
async def stop_process():
    """Stop the Agent Runner process."""
    import sys
    async def _exit():
        await asyncio.sleep(1)
        sys.exit(0)
    
    asyncio.create_task(_exit())
    logger.warning("Agent Runner process termination requested.")
    return {"ok": True, "message": "Agent Runner stopping in 1s..."}
