import logging
import time
import json
import asyncio
import aiofiles
import yaml
from typing import Dict, Any, Optional
from fastapi import APIRouter, Body, Request, HTTPException, Depends
from pathlib import Path

from agent_runner.agent_runner import get_shared_state, get_shared_engine
from agent_runner.state import AgentState
from agent_runner.background_tasks import get_task_manager
from agent_runner.constants import MODEL_ROLES
from common.observability import get_observability
from agent_runner.db_utils import run_query

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

@router.get("/admin/ingestion/status")
async def get_ingestion_status():
    """Return status of the RAG ingestion pipeline."""
    from agent_runner.rag_ingestor import INGEST_DIR
    pause_file = INGEST_DIR / ".paused"
    is_paused = pause_file.exists()
    reason = ""
    if is_paused:
        try:
            reason = pause_file.read_text().strip()
        except Exception as e:
            logger.debug(f"Could not read pause reason: {e}")
            reason = "Manual Pause"
            
    return {
        "ok": True,
        "paused": is_paused,
        "reason": reason,
        "ingest_dir": str(INGEST_DIR)
    }

@router.post("/admin/ingestion/resume")
async def resume_ingestion():
    """Resume a paused ingestion pipeline."""
    from agent_runner.rag_ingestor import INGEST_DIR
    pause_file = INGEST_DIR / ".paused"
    if pause_file.exists():
        try:
            pause_file.unlink()
            logger.info("Ingestion resumed by user request.")
            return {"ok": True, "message": "Ingestion resumed"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    return {"ok": True, "message": "Ingestion was not paused"}

@router.post("/admin/ingestion/pause")
async def pause_ingestion():
    """Manually pause the ingestion pipeline."""
    from agent_runner.rag_ingestor import INGEST_DIR
    pause_file = INGEST_DIR / ".paused"
    try:
        pause_file.write_text("Manual Pause")
        logger.info("Ingestion paused by user request.")
        return {"ok": True, "message": "Ingestion paused"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/admin/ingestion/clear-and-resume")
async def clear_and_resume_ingestion():
    """Delete the problem file that caused the pause and resume."""
    from agent_runner.rag_ingestor import INGEST_DIR
    pause_file = INGEST_DIR / ".paused"
    if not pause_file.exists():
        return {"ok": False, "message": "Not paused"}
    
    try:
        reason = pause_file.read_text().strip()
        # Extract filename: "Quality Check Failed: filename.ext - ..."
        import re
        match = re.search(r"Failed: (.*?) -", reason)
        if match:
            filename = match.group(1)
            file_path = INGEST_DIR / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted problem file: {filename}")
        
        pause_file.unlink()
        return {"ok": True, "message": "Problem file cleared and ingestion resumed"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/admin/memory/status")
async def get_memory_status():
    """Detailed status of the Memory Engine (SurrealDB)."""
    state = get_shared_state()
    # Check SurrealDB health
    import aiohttp
    db_ok = False
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health", timeout=1.0) as resp:
                db_ok = resp.status == 200
    except Exception as e:
        logger.debug(f"Database health check failed: {e}")
        db_ok = False
        
    return {
        "ok": True,
        "active": db_ok,
        "engine": "SurrealDB",
        "mode": "Transactional (HNSW Enabled)" if db_ok else "Offline"
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

@router.get("/admin/startup-status")
async def startup_status():
    """
    Get the startup status message that was generated during system initialization.
    Useful when no chat client was connected during startup.
    """
    state = get_shared_state()
    if hasattr(state, 'startup_status') and state.startup_status:
        return {
            "ok": True,
            "startup_status": state.startup_status,
            "available": True
        }
    else:
        return {
            "ok": False,
            "message": "Startup status not available (system may not have completed startup)",
            "available": False
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
        except Exception as e:
            logger.debug(f"URL check failed for {url}: {e}")
            return False

    # Check Ollama (Port 11434)
    ollama_ok = await _check_url("http://localhost:11434")
    
    # Check Database (SurrealDB Port 8000)
    # Surreal's health endpoint is /health or /status usually, or just root
    db_ok = await _check_url("http://localhost:8000/health") 
    
    # Internet is updated by background task, which is acceptable cache
    internet_status = "Connected" if state.internet_available else "Offline"
    
    # CPU and memory metrics (using psutil if available)
    try:
        import psutil
        process = psutil.Process()
        cpu_percent = process.cpu_percent(interval=0.1)
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        memory_percent = process.memory_percent()
        
        # Categorize CPU usage
        if cpu_percent < 25:
            cpu_status = "Low"
        elif cpu_percent < 75:
            cpu_status = "Moderate"
        else:
            cpu_status = "High"
        
        # Categorize memory usage
        if memory_percent < 50:
            memory_status = "Optimal"
        elif memory_percent < 80:
            memory_status = "Moderate"
        else:
            memory_status = "High"
        
        cpu_usage = f"{cpu_status} ({cpu_percent:.1f}%)"
        memory_info_str = f"{memory_status} ({memory_mb:.1f} MB, {memory_percent:.1f}%)"
    except ImportError:
        cpu_usage = "Unavailable (psutil not installed)"
        memory_info_str = "Unavailable (psutil not installed)"
    except Exception as metrics_err:
        logger.debug(f"Failed to get system metrics: {metrics_err}")
        cpu_usage = "Error"
        memory_info_str = "Error"
    
    return {
        "ok": True,
        "mode": state.system_mode, # Production/Dev
        "active_mode": state.active_mode, # Chat/Coding
        "internet": internet_status,
        "hardware_verified": state.hardware_verified,
        "cpu_usage": cpu_usage,
        "memory_info": memory_info_str,
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
    
    for key in MODEL_ROLES:
        if key in config:
            setattr(state, key, config[key])

    await save_system_config(state)
    
    # Return current state of all models
    current_models = {k: getattr(state, k) for k in MODEL_ROLES}
    return {"ok": True, "models": current_models}

@router.post("/admin/config/update")
async def update_single_config(body: Dict[str, Any] = Body(...)):
    """
    Update a single configuration value or secret.
    Body: { "key": "VISION_MODEL", "value": "...", "type": "config"|"secret" }
    """
    state = get_shared_state()
    key = body.get("key")
    value = body.get("value")
    ctype = body.get("type", "secret")
    
    if not key:
        raise HTTPException(status_code=400, detail="Missing key")

    # Use ConfigManager
    if ctype == "secret":
        success = await state.config_manager.set_secret(key, value)
    else:
        # Config / Model
        success = await state.config_manager.set_config_value(key, value)
        
    if success:
        return {"ok": True, "message": f"Updated {key} ({ctype})"}
    else:
        return {"ok": False, "error": "Failed to update configuration"}

async def save_system_config(state):
    """Save current state to system_config.json for persistence."""
    try:
        config_path = Path(__file__).parent.parent.parent / "system_config.json"
        
        # Load existing to avoid overwriting unrelated settings
        cfg = {}
        if config_path.exists():
            async with aiofiles.open(config_path, "r") as f:
                content = await f.read()
                cfg = json.loads(content)
        
        # Update all 13 Roles
        cfg.update({k: getattr(state, k) for k in MODEL_ROLES})

        async with aiofiles.open(config_path, "w") as f:
            await f.write(json.dumps(cfg, indent=4))
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

@router.get("/admin/dashboard/state")
async def get_dashboard_state():
    """Aggregate system state for the V2 Dashboard."""
    state = get_shared_state()
    
    # 1. Health & Topology
    from agent_runner.health_monitor import get_detailed_health_report
    health = await get_detailed_health_report()
    
    # 2. Ingestion Status
    ingest_status = await get_ingestion_status()
    
    # 3. Circuit Breakers
    breakers = state.mcp_circuit_breaker.get_status()
    open_breakers = [b for b in breakers.values() if b["state"] == "open"]
    
    # 4. Memory Stats (Simplified)
    # We could call get_memory_stats() but let's keep it fast
    mem_active = hasattr(state, "memory") and state.memory is not None
    
    # 5. Budget (Real implementation)
    try:
        from common.budget import get_budget_tracker
        tracker = get_budget_tracker()
        budget = {
            "percent_used": (tracker.current_spend / tracker.daily_limit_usd * 100) if tracker.daily_limit_usd > 0 else 0,
            "current_spend": tracker.current_spend,
            "daily_limit_usd": tracker.daily_limit_usd
        }
    except Exception as budget_err:
        logger.warning(f"Failed to load budget: {budget_err}")
        budget = {
            "percent_used": 0,
            "current_spend": 0.0,
            "daily_limit_usd": 50.0
        }
        
    return {
        "status": health.get("status", "healthy"),
        "ingestion": ingest_status,
        "memory_stats": {"active": mem_active, "mode": "Transactional" if mem_active else "Offline"},
        # "budget": budget,  # Removed - not implemented
        "metrics": health.get("metrics", {}),
        "summary": {
            "critical_count": len(open_breakers),
            "open_breakers": open_breakers,
            "overall_status": breakers,
            "latest_anomaly": None # Telemetry will populate this via other channels
        }
    }

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
    log_file = "logs/agent_runner.log"
    if not Path(log_file).exists():
        return {"ok": False, "error": "Log file not found"}
    
    try:
        from collections import deque
        # Read file asynchronously
        async with aiofiles.open(log_file, "r", encoding="utf-8", errors="replace") as f:
            all_lines = await f.readlines()
            lines_list = list(deque(all_lines, maxlen=lines))
        return {"ok": True, "logs": [l.rstrip() for l in lines_list]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# Note: sse_starlette.sse.EventSourceResponse was removed to avoid dependency
# Using FastAPI's StreamingResponse instead

@router.get("/admin/llm/roles")
async def get_llm_roles():
    state = get_shared_state()
    # Attempt to load defaults from config.yaml for comparison
    defaults = {
         "agent_model": "openai:gpt-4o-mini",
         "task_model": "ollama:mistral:latest", 
         "router_model": "ollama:mistral:latest",
         "summarization_model": "openai:gpt-4o",
         "vision_model": "openai:gpt-4o",
         "mcp_model": "openai:gpt-4o-mini",
         "finalizer_model": "openai:gpt-4o",
         "fallback_model": "ollama:mistral:latest",
         "intent_model": "ollama:mistral:latest",
         "pruner_model": "ollama:mistral:latest",
         "healer_model": "openai:gpt-4o",
         "critic_model": "openai:gpt-4o",
         "embedding_model": "ollama:mxbai-embed-large:latest"
    }
    # NOTE: Removed config.yaml read - database is source of truth
    # If defaults are needed, they should come from database or be hardcoded constants

    return {
        "ok": True,
        "roles": {k: getattr(state, k) for k in MODEL_ROLES},
        "defaults": defaults
    }

@router.post("/admin/llm/roles")
async def update_llm_roles(request: Request):
    state = get_shared_state()
    try:
        data = await request.json()
        # Use MODEL_ROLES constant instead of individual if statements
        for key in MODEL_ROLES:
            if key in data:
                setattr(state, key, data[key])
        
        await save_system_config(state)
        return {"ok": True, "message": "Roles updated successfully"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/admin/system/process/stop")
async def stop_process():
    """Stop the Agent Runner process."""
    import sys
    async def _exit():
        from agent_runner.constants import SLEEP_STREAM_POLL
        await asyncio.sleep(1)  # Exit delay - keep as 1 second
        sys.exit(0)
    
    asyncio.create_task(_exit())
    logger.warning("Agent Runner process termination requested.")
    return {"ok": True, "message": "Agent Runner stopping in 1s..."}

@router.get("/admin/mcp/server/status")
async def get_mcp_server_status():
    """Get status of the internal MCP Server (SSE)."""
    from agent_runner.mcp_server.router import transport
    
    active_sessions = []
    if transport:
        for sid, session in transport.sessions.items():
            if session.active:
                active_sessions.append({
                    "id": sid,
                    "name": session.client_name,
                    "client_info": session.client_info
                })
            
    return {
        "active": True, # Always active if runner is up
        "port": 5460, # Standard Agent Port
        "protocol": "sse",
        "clients": active_sessions
    }

@router.get("/admin/logs/stream")
async def stream_logs(request: Request, services: str = "agent_runner"):
    """
    Stream logs via SSE using native StreamingResponse.
    Tail relevant log files and emit lines as they are written.
    """
    import os
    from fastapi.responses import StreamingResponse
    import json
    
    async def event_generator():
        files_map = {
            "agent_runner": "agent_runner.log",
            "router": "router.log"
        }
        
        target_files = []
        try:
            for svc in services.split(","):
                if svc in files_map:
                    try:
                        target_files.append((svc, open(files_map[svc], "r")))
                    except FileNotFoundError:
                        pass
            
            # Seek to end
            for _, f in target_files:
                f.seek(0, os.SEEK_END)
            
            while True:
                if await request.is_disconnected():
                    break
                    
                has_data = False
                for svc, f in target_files:
                    line = f.readline()
                    if line:
                        yield f"data: {json.dumps({'service': svc, 'line': line.strip()})}\n\n"
                        has_data = True
                
                from agent_runner.constants import SLEEP_STREAM_POLL
                if not has_data:
                    await asyncio.sleep(SLEEP_STREAM_POLL)
        finally:
            # Ensure all file handles are closed
            for _, f in target_files:
                try:
                    f.close()
                except (OSError, IOError) as file_err:
                    logger.debug(f"Failed to close log file: {file_err}")
                    pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/admin/system/restart")
async def restart_system_endpoint():
    """Trigger a full system restart script."""
    import os
    from agent_runner.config import PROJECT_ROOT
    
    script_path = f"{PROJECT_ROOT}/bin/restart_all.sh"
    
    # Check if script exists
    if not os.path.exists(script_path):
        # Fallback to just failing/stopping (Supervisor should restart)
        return await stop_process()
        
    try:
        # Spawn detached
        import subprocess
        subprocess.Popen([script_path], cwd=os.path.dirname(script_path), start_new_session=True)
        return {"ok": True, "message": "System restart triggered"}
    except Exception as e:
         logger.error(f"Failed to trigger restart: {e}")
         return {"ok": False, "error": str(e)}

@router.get("/admin/diagnostics/stream")
async def stream_diagnostics(request: Request):
    """
    Stream diagnostic logs directly from the diagnostic_log table.
    
    NOTE: This endpoint is currently UNUSED - there is no diagnostics tab in the UI.
    live_stream.md is a log file only - it should not be read for UI purposes.
    If a diagnostics UI is added in the future, this endpoint is ready to use.
    """
    from fastapi.responses import StreamingResponse
    import os
    import httpx
    
    async def diag_generator():
        # Read directly from diagnostic_log table instead of live_stream.md
        # live_stream.md is a log file only, not for UI consumption
        surreal_url = os.getenv("SURREAL_URL", "http://localhost:8000")
        surreal_ns = os.getenv("SURREAL_NS", "orchestrator")
        surreal_db = os.getenv("SURREAL_DB", "memory")
        surreal_user = os.getenv("SURREAL_USER", "root")
        surreal_pass = os.getenv("SURREAL_PASS", "root")
        
        last_timestamp = time.time()
        
        async with httpx.AsyncClient() as client:
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    # Query for new logs since last check
                    query = (
                        f"USE NS {surreal_ns}; USE DB {surreal_db}; "
                        f"SELECT * FROM diagnostic_log "
                        f"WHERE timestamp > {last_timestamp} "
                        f"ORDER BY timestamp ASC LIMIT 50;"
                    )
                    
                    resp = await client.post(
                        f"{surreal_url}/sql",
                        content=query,
                        auth=(surreal_user, surreal_pass),
                        headers={"Accept": "application/json"},
                        timeout=5.0
                    )
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, list):
                            for item in data:
                                if item.get("status") == "OK" and isinstance(item.get("result"), list):
                                    for log_entry in item.get("result", []):
                                        timestamp = log_entry.get("timestamp", 0)
                                        if timestamp > last_timestamp:
                                            last_timestamp = timestamp
                                        
                                        # Format log entry
                                        service = log_entry.get("service", "unknown")
                                        level = log_entry.get("level", "INFO")
                                        message = log_entry.get("message", "")
                                        iso_time = log_entry.get("iso_time", "")
                                        
                                        formatted = f"{iso_time} [{level}] {service}: {message}"
                                        yield f"data: {json.dumps({'line': formatted})}\n\n"
                
                except Exception as e:
                    logger.debug(f"Diagnostics stream error: {e}")
                
                from agent_runner.constants import SLEEP_STREAM_POLL
                await asyncio.sleep(1.0)  # Diagnostics stream delay
                     
    return StreamingResponse(diag_generator(), media_type="text/event-stream")

@router.post("/admin/tools/execute")
async def execute_tool_endpoint(body: Dict[str, Any] = Body(...)):
    """
    Directly execute a defined tool/function.
    Body: { "tool_name": "list_dir", "arguments": {"path": "."} }
    """
    state = get_shared_state()
    engine = get_shared_engine()
    tool_name = body.get("tool_name")
    args = body.get("arguments", {})
    
    if not tool_name:
         return {"ok": False, "error": "Missing tool_name"}

    if hasattr(engine, "executor"):
        # We wrap in the standard executor call
        # Mock a tool call object
        tool_call = {
            "function": {
                "name": tool_name,
                "arguments": json.dumps(args)
            }
        }
        try:
            result = await engine.executor.execute_tool_call(tool_call, request_id="admin-debug", user_query="")
            return {"ok": True, "result": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    else:
        return {"ok": False, "error": f"Executor not ready. Engine: {engine}, Dir: {dir(engine)}"}

@router.get("/admin/registry/health")
async def registry_health(state: AgentState = Depends(get_shared_state)):
    """
    Check registry integrity and return validation status.
    """
    try:
        from agent_runner.maintenance_tasks import validate_registry_integrity
        result = await validate_registry_integrity(state)
        return result
    except Exception as e:
        logger.error(f"Registry health check failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e), "issues": [], "warnings": []}


@router.get("/admin/task-health")
async def task_health(state: AgentState = Depends(get_shared_state)):
    """
    Get health statistics for fire-and-forget tasks.
    """
    from agent_runner.task_utils import get_task_health_summary
    summary = await get_task_health_summary()
    return {"ok": True, "task_health": summary}


@router.post("/admin/validate-changes")
async def validate_changes():
    """
    Validate all recent changes (last 2 hours).
    Tests tool categorization, evaluation, registry, rating integration, and marketplace.
    """
    from agent_runner.tests.validate_recent_changes import validate_all_changes
    return await validate_all_changes()


@router.post("/admin/chat-latency-test")
async def chat_latency_test(
    iterations: int = Body(5, embed=True),
    test_message: Optional[str] = Body(None, embed=True)
):
    """
    Run comprehensive chat interface latency test with component breakdown.
    """
    try:
        from agent_runner.tools.chat_latency_test import tool_run_chat_latency_test
        state = get_shared_state()
        return await tool_run_chat_latency_test(state, iterations, test_message)
    except ImportError:
        # Fallback to direct implementation if import fails
        from agent_runner.tools.chat_latency_test import tool_run_chat_latency_test as _run_test
        state = get_shared_state()
        return await _run_test(state, iterations, test_message)
