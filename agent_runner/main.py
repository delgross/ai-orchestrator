import asyncio
import time
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from agent_runner.state import AgentState
from agent_runner.engine import AgentEngine
from agent_runner.config import load_mcp_servers, load_agent_runner_limits
from agent_runner.tasks import internet_check_task, stdio_process_health_monitor
from agent_runner.background_tasks import get_task_manager, TaskPriority
from agent_runner.health_monitor import initialize_health_monitor, health_check_task
from agent_runner.memory_tasks import memory_consolidation_task, memory_backup_task, optimize_memory_task, memory_audit_task
from agent_runner.rag_ingestor import rag_ingestion_task
from agent_runner.dashboard_tracker import get_dashboard_tracker, DashboardErrorType
from common.observability import ComponentType, get_observability
from common.observability_middleware import ObservabilityMiddleware
from common.constants import (
    OBJ_CHAT_COMPLETION,
    OBJ_MODEL,
    ROLE_SYSTEM,
    ROLE_USER,
    ROLE_ASSISTANT
)
from common.logging_setup import setup_logger

from contextlib import asynccontextmanager

logger = logging.getLogger("agent_runner")

@asynccontextmanager
async def log_time(operation_name: str, level=logging.DEBUG):
    t0 = time.time()
    try:
        yield
    finally:
        duration = time.time() - t0
        logger.log(level, f"PERF: {operation_name} completed in {duration:.4f}s")

app = FastAPI(title="Agent Runner (Modularized)")

# State and Engine instances
state = AgentState()
engine = AgentEngine(state)

# CORS Configuration for Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In prod, restrict to ROUTER_BASE
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.add_middleware(
    ObservabilityMiddleware,
    component_type=ComponentType.AGENT_RUNNER,
    component_id="agent-runner-main"
)

@app.on_event("startup")
async def on_startup():
    setup_logger("agent_runner")
    # Redirect tracking logs to the main agent runner log
    setup_logger("unified_tracking", log_file="agent_runner.log")
    setup_logger("logging_utils", log_file="agent_runner.log")
    setup_logger("common.circuit_breaker", log_file="agent_runner.log")
    await load_mcp_servers(state)
    load_agent_runner_limits(state)
    
    # Run startup backup for data safety
    try:
        from agent_runner.memory_tasks import memory_backup_task
        await memory_backup_task(state)
    except Exception as e:
        setup_logger("agent_runner").error(f"Startup backup failed: {e}")
    
    # Initialize and start background tasks
    task_manager = get_task_manager()
    
    # Initialize Health Monitor with runtime dependencies
    initialize_health_monitor(
        mcp_servers=state.mcp_servers,
        mcp_circuit_breaker=state.mcp_circuit_breaker,
        gateway_base=state.gateway_base,
        http_client=await state.get_http_client(),
        state=state
    )
    
    # Register periodic tasks
    def is_idle() -> bool:
        """System is idle if no active requests and quiet since last interaction."""
        quiet_threshold = 15.0 # seconds
        idle_duration = time.time() - state.last_interaction_time
        is_quiet = idle_duration > quiet_threshold
        is_inactive = state.active_requests == 0
        return is_inactive and is_quiet

    task_manager.set_idle_checker(is_idle)
    
    task_manager.register(
        name="internet_check",
        func=lambda: internet_check_task(state),
        interval=state.config.get("system", {}).get("internet_check_interval", 15),
        description="Check internet connectivity",
        priority=TaskPriority.HIGH
    )
    
    task_manager.register(
        name="stdio_monitor",
        func=lambda: stdio_process_health_monitor(state),
        interval=60,
        description="Monitor stdio process health",
        priority=TaskPriority.HIGH
    )
    
    task_manager.register(
        name="health_check",
        func=health_check_task,
        interval=60,
        description="Comprehensive system health check",
        priority=TaskPriority.HIGH
    )
    
    task_manager.register(
        name="memory_consolidation",
        func=lambda: memory_consolidation_task(state),
        interval=300, # Run every 5 minutes
        description="Autonomous fact extraction from conversation logs",
        priority=TaskPriority.LOW,
        idle_only=True
    )
    
    task_manager.register(
        name="memory_backup",
        func=lambda: memory_backup_task(state),
        interval=3600, # Run hourly
        description="Hourly SQL export of memory database",
        priority=TaskPriority.LOW,
        idle_only=True
    )
    
    task_manager.register(
        name="memory_optimization",
        func=lambda: optimize_memory_task(state),
        interval=43200, # Run every 12 hours
        description="Integrity check and optimization for memory database",
        priority=TaskPriority.LOW,
        idle_only=True
    )

    task_manager.register(
        name="memory_audit",
        func=lambda: memory_audit_task(state),
        interval=1800, # Run every 30 minutes
        description="Reflective fact checking and confidence updates",
        priority=TaskPriority.LOW,
        idle_only=True
    )

    task_manager.register(
        name="rag_ingestion",
        func=lambda: rag_ingestion_task("http://127.0.0.1:5555", state),
        interval=10, # Check every 10 seconds for responsiveness
        description="Auto-ingestion of files into RAG server",
        priority=TaskPriority.LOW,
        idle_only=True
    )

    from agent_runner.maintenance_tasks import code_janitor_task, auto_tagger_task, graph_optimization_task, morning_briefing_task, daily_research_task, stale_memory_pruner_task, visual_sentry_task

    # ... (existing registrations) ...

    task_manager.register(
        name="visual_sentry",
        func=lambda: visual_sentry_task(state),
        interval=3600, # Hourly security/defect check
        description="Detects visual anomalies against reference images",
        priority=TaskPriority.LOW,
        idle_only=True
    )

    task_manager.register(
        name="graph_optimizer",
        func=lambda: graph_optimization_task(state),
        interval=43200, # Nightly
        priority=TaskPriority.LOW,
        idle_only=True
    )

    task_manager.register(
        name="morning_briefing",
        func=lambda: morning_briefing_task(state),
        interval=86400, # Daily 
        description="Daily system status report",
        priority=TaskPriority.LOW,
        idle_only=True
    )

    task_manager.register(
        name="daily_research",
        func=lambda: daily_research_task(state),
        interval=43200, 
        description="Autonomous topic research",
        priority=TaskPriority.LOW,
        idle_only=True
    )
    
    task_manager.register(
        name="stale_pruner",
        func=lambda: stale_memory_pruner_task(state),
        interval=604800, # Weekly
        description="Cleanup low-confidence memories",
        priority=TaskPriority.LOW,
        idle_only=True
    )

    from agent_runner.maintenance_tasks import morning_briefing_task, stale_memory_pruner_task, daily_research_task
    
    task_manager.register(
        name="morning_briefing",
        func=lambda: morning_briefing_task(state),
        interval=86400, # Daily 
        description="Daily system status report",
        priority=TaskPriority.LOW,
        idle_only=True
    )

    task_manager.register(
        name="daily_research",
        func=lambda: daily_research_task(state),
        interval=43200, # Twice Daily check
        description="Autonomous topic research",
        priority=TaskPriority.LOW,
        idle_only=True
    )
    
    # Stale Pruner (Low Priority Weeklies)
    task_manager.register(
        name="stale_pruner",
        func=lambda: stale_memory_pruner_task(state),
        interval=604800, # Weekly
        description="Cleanup low-confidence memories",
        priority=TaskPriority.LOW,
        idle_only=True
    )
    
    await task_manager.start()
    
    # One-off tasks (still manual since they are just startup triggers)
    asyncio.create_task(engine.discover_mcp_tools())
    
    logger.info(f"Agent Runner started with AGENT_MODEL='{state.agent_model}'")
    logger.info(f"Task Model: '{state.task_model}'")

@app.on_event("shutdown")
async def on_shutdown():
    await get_task_manager().stop()
    await state.close_http_client()
    logger.info("Agent Runner shutting down.")

@app.get("/")
async def root():
    return {
        "service": "agent-runner",
        "status": "online",
        "ok": True, # Dashboard expectation
        "model": state.agent_model,
        "agent_model": state.agent_model, # Alias for board
        "mcp_servers": list(state.mcp_servers.keys()),
        "uptime_s": time.time() - state.started_at,
        "version": "1.0.0-modular"
    }

@app.post("/v1/chat/completions")
async def chat_completions(body: Dict[str, Any], request: Request):
    messages = body.get("messages", [])
    if not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="messages must be a list")
    
    # Extract Request ID for distributed tracing
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        import uuid
        request_id = str(uuid.uuid4())[:8]

    # Use the engine to process the request
    state.active_requests += 1
    state.last_interaction_time = time.time()
    
    # Timer for stats endpoint (distinct from log_time)
    t0_stats = time.time()
    
    try:
        requested_model = body.get(OBJ_MODEL)
        
        logger.info(f"REQ [{request_id}] Agent Execution: Model='{requested_model}'")

        # Prevent infinite recursion / invalid model names
        if requested_model == "agent:mcp" or not requested_model or ":" not in requested_model:
            requested_model = None
            
        completion = {}
        async with log_time(f"Agent Loop [{request_id}]", level=logging.INFO):
            completion = await engine.agent_loop(messages, model=requested_model, request_id=request_id)
        
        # Update Stats
        duration_ms = (time.time() - t0_stats) * 1000
        state.request_count += 1
        state.total_response_time_ms += duration_ms

    except Exception as e:
        logger.error(f"Agent Execution Failed [{request_id}]: {e}", exc_info=True)
        state.error_count += 1
        state.last_error = str(e)
        raise e
    finally:
        state.active_requests -= 1
        state.last_interaction_time = time.time()
    
    completion[OBJ_MODEL] = body.get(OBJ_MODEL, "agent:mcp")
    completion.setdefault("created", int(time.time()))
    completion.setdefault("object", OBJ_CHAT_COMPLETION)
    completion.setdefault("id", f"chatcmpl-{int(time.time() * 1000)}")
    
    return JSONResponse(completion)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ok": True,
        "internet": state.internet_available,
        "uptime_s": time.time() - state.started_at
    }

@app.get("/metrics")
async def metrics():
    avg_latency = 0
    if state.request_count > 0:
        avg_latency = state.total_response_time_ms / state.request_count
        
    return {
        "ok": True,
        "requests": state.request_count,
        "errors": state.error_count,
        "avg_latency_ms": round(avg_latency, 2),
        "last_error": state.last_error
    }

@app.get("/admin/system-status")
async def system_status():
    # Mocking hardware data for dashboard KPI
    ollama_ok = False
    if hasattr(state, "mcp_circuit_breaker"):
        ollama_ok = state.mcp_circuit_breaker.is_allowed("ollama")
    
    return {
        "ok": True,
        "mode": state.system_mode,
        "internet": "Connected" if state.internet_available else "Offline",
        "hardware_verified": state.hardware_verified,
        "cpu_usage": "Low", # Simplified
        "memory_info": "Optimal",
        "ollama_ok": ollama_ok,
        "limits": {
            "max_read": state.max_read_bytes,
            "max_list": state.max_list_entries
        }
    }

@app.post("/admin/config/models")
async def update_models(config: Dict[str, str] = Body(...)):
    """Update system models dynamically."""
    import json
    from pathlib import Path
    import os

    if "summarization_model" in config: state.summarization_model = config["summarization_model"]
    if "agent_model" in config: state.agent_model = config["agent_model"]
    if "task_model" in config: state.task_model = config["task_model"]
    if "router_model" in config: state.router_model = config["router_model"]

    # Save Persistence
    try:
        config_path = Path("ai/system_config.json")
        if not config_path.is_absolute():
            config_path = Path(os.getcwd()) / "ai" / "system_config.json"
        
        with open(config_path, "w") as f:
            json.dump({
                "agent_model": state.agent_model,
                "summarization_model": state.summarization_model,
                "task_model": state.task_model,
                "router_model": state.router_model
            }, f, indent=2)
    except Exception as e:
        print(f"Failed to save system_config.json: {e}")

    return {
        "ok": True, 
        "models": {
            "summarization_model": state.summarization_model,
            "agent_model": state.agent_model,
            "task_model": state.task_model,
            "router_model": state.router_model
        }
    }

@app.post("/admin/tasks/consolidation")
async def trigger_consolidation():
    """Manually trigger memory consolidation."""
    from agent_runner.memory_tasks import memory_consolidation_task
    # Run as background task to avoid blocking response? 
    # Or await? Awaiting ensures it starts. 
    # But it might be slow (LLM calls).
    # Better to run in background.
    asyncio.create_task(memory_consolidation_task(state))
    return {"ok": True, "message": "Memory consolidation triggered in background"}

@app.get("/admin/circuit-breaker/status")
async def circuit_breaker_status():
    return {
        "ok": True,
        "breakers": state.mcp_circuit_breaker.get_status()
    }

@app.post("/admin/circuit-breaker/reset/{name}")
async def reset_circuit_breaker(name: str):
    state.mcp_circuit_breaker.reset(name)
    return {"ok": True, "message": f"Circuit breaker '{name}' reset"}

@app.post("/admin/circuit-breaker/reset-all")
async def reset_all_circuit_breakers():
    state.mcp_circuit_breaker.reset_all()
    # Reset cooldowns too if implemented
    return {"ok": True, "message": "All circuit breakers reset"}

@app.post("/admin/telemetry/log")
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

@app.get("/admin/background-tasks")
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

@app.post("/admin/reload-mcp")
async def reload_mcp():
    load_mcp_servers(state)
    return {"ok": True, "message": "MCP servers reloaded"}

@app.get("/admin/system-prompt")
async def get_system_prompt():
    prompt = await engine.get_system_prompt()
    return {"ok": True, "prompt": prompt}

@app.get("/admin/memory/facts")
async def get_memory_facts(query: str = "", limit: int = 100):
    from agent_runner.tools.mcp import tool_mcp_proxy
    # Semantic search if query provided, otherwise get stats or list
    if query:
        res = await tool_mcp_proxy(state, "project-memory", "semantic_search", {"query": query, "limit": limit})
    else:
        # Fallback to general stats or listing if project-memory supports it
        res = await tool_mcp_proxy(state, "project-memory", "get_memory_stats", {})
    return res

@app.get("/admin/mcp/tools")
async def get_all_mcp_tools(server: str = None):
    """Return discovered MCP tools, optionally filtered by server."""
    cache = engine.mcp_tool_cache
    if server:
        if server in cache:
            return {"ok": True, "server": server, "tools": cache[server]}
        else:
            return {"ok": False, "error": "Server not found in cache", "server": server}
    
    # Return all
    return {"ok": True, "tools": cache}

@app.get("/admin/dashboard/insights")
async def get_dashboard_insights():
    tracker = get_dashboard_tracker()
    return {"ok": True, "insights": tracker.get_learning_insights()}

@app.post("/admin/dashboard/track/error")
async def track_dashboard_error(body: Dict[str, Any]):
    tracker = get_dashboard_tracker()
    tracker.record_error(
        error_type=DashboardErrorType(body.get("type", "unknown")),
        error_message=body.get("message", "No message provided"),
        error_stack=body.get("stack"),
        url=body.get("url"),
        user_agent=body.get("user_agent"),
        component=body.get("component"),
        context=body.get("context"),
        request_id=body.get("request_id")
    )
    return {"ok": True}

@app.post("/admin/dashboard/track/interaction")
async def track_dashboard_interaction(body: Dict[str, Any]):
    tracker = get_dashboard_tracker()
    tracker.record_interaction(
        action=body.get("action", "unknown"),
        target=body.get("target"),
        success=body.get("success", True),
        duration_ms=body.get("duration_ms"),
        context=body.get("context")
    )
    return {"ok": True}

@app.get("/admin/logs/tail")
async def get_logs_tail(lines: int = 100):
    """Return the last N lines of the agent runner log."""
    import os
    log_file = os.path.expanduser("~/Library/Logs/ai/agent_runner.err.log")
    try:
        # Use simple os/file reading, inefficient for huge files but ok here
        with open(log_file, 'r') as f:
            # Read all lines then slice (simple) - for very large files use seeks, but log rotation should exist
            content = f.readlines()
            return {"ok": True, "logs": content[-lines:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/admin/roles")
async def get_llm_roles():
    """Get the current model assignments for various system roles."""
    return {
        "ok": True,
        "roles": {
            "agent_model": state.agent_model,
            "task_model": state.task_model,
            "mcp_model": state.mcp_model,
            "router_model": state.router_model,
            "summarization_model": state.summarization_model,
            "finalizer_model": state.finalizer_model,
            "finalizer_model": state.finalizer_model,
            "fallback_model": state.fallback_model,
            "embedding_model": state.embedding_model,
            "vision_model": state.vision_model
        },
        "flags": {
            "finalizer_enabled": state.finalizer_enabled
        }
    }

@app.post("/admin/roles")
async def update_llm_roles(request: Request):
    """Update runtime model assignments."""
    body = await request.json()
    updates = body.get("updates", {})
    flags = body.get("flags", {})
    
    if "agent_model" in updates: state.agent_model = updates["agent_model"]
    if "task_model" in updates: state.task_model = updates["task_model"]
    if "mcp_model" in updates: state.mcp_model = updates["mcp_model"]
    if "router_model" in updates: state.router_model = updates["router_model"]
    if "summarization_model" in updates: state.summarization_model = updates["summarization_model"]
    if "finalizer_model" in updates: state.finalizer_model = updates["finalizer_model"]
    if "fallback_model" in updates: state.fallback_model = updates["fallback_model"]
    if "vision_model" in updates: state.vision_model = updates["vision_model"]
    
    if "embedding_model" in updates:
        state.embedding_model = updates["embedding_model"]
        # Sync to Router
        try:
            client = await state.get_http_client()
            # Note: gateway_base includes /v1 sometimes? No, state.py says rstrip('/'). Defaults to 5455.
            # But we need /admin path.
            # URL: http://127.0.0.1:5455/admin/llm/embedding/default?model=...
            # Note: if gateway_base is http://127.0.0.1:5455, then:
            await client.post(f"{state.gateway_base}/admin/llm/embedding/default", params={"model": state.embedding_model})
        except Exception as e:
            logger.warning(f"Failed to sync embedding model to Router: {e}")

    if "finalizer_enabled" in flags: state.finalizer_enabled = flags["finalizer_enabled"]
    
    return {"ok": True, "roles": {
        "agent_model": state.agent_model,
        "task_model": state.task_model,
        "mcp_model": state.mcp_model,
        "router_model": state.router_model,
        "summarization_model": state.summarization_model,
        "finalizer_model": state.finalizer_model,
        "fallback_model": state.fallback_model,
        "embedding_model": state.embedding_model,
        "vision_model": state.vision_model
    }}

@app.get("/admin/docs/list")
async def list_documentation_files():
    """List markdown files in the ai/docs directory."""
    import os
    import glob
    
    docs_dir = os.path.expanduser("~/Sync/Antigravity/ai/docs")
    if not os.path.exists(docs_dir):
        try:
            os.makedirs(docs_dir, exist_ok=True)
            # Create a README
            with open(f"{docs_dir}/README.md", "w") as f:
                f.write("# Documentation\n\nDrop markdown files here to view them in the dashboard.")
        except: pass
        
    try:
        files = glob.glob(f"{docs_dir}/*.md")
        return {"ok": True, "files": [{"name": os.path.basename(f), "path": f} for f in files]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/admin/docs/read")
async def read_documentation_file(path: str):
    import os
    # Security check: must be in docs dir
    docs_dir = os.path.expanduser("~/Sync/Antigravity/ai/docs")
    abs_path = os.path.abspath(path)
    if not abs_path.startswith(docs_dir):
        return {"ok": False, "error": "Access denied"}
        
    try:
        with open(abs_path, 'r') as f:
            return {"ok": True, "content": f.read()}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# --- Notification Endpoints ---
@app.get("/admin/notifications")
async def get_notifications(priority: str = None, unread: bool = False, limit: int = 50):
    from common.notifications import get_notification_manager, NotificationLevel
    nm = get_notification_manager()
    
    level_filter = None
    if priority:
        try:
            level_filter = NotificationLevel(priority.lower())
        except: pass
        
    notifs = nm.get_notifications(
        level=level_filter,
        unacknowledged_only=unread,
        limit=limit
    )
    
    # Convert to JSON-able dicts
    return {"ok": True, "notifications": [
        {
            "level": n.level.value,
            "title": n.title,
            "message": n.message,
            "category": n.category,
            "timestamp": n.timestamp,
            "acknowledged": n.acknowledged,
            "id": i # Index as pseudo-ID for now
        } 
        for i, n in enumerate(nm.notifications) # Ideally notifications should have stable IDs, but index works for in-memory
        if n in notifs
    ]}

@app.post("/admin/notifications/acknowledge")
async def acknowledge_all_notifications():
    from common.notifications import get_notification_manager
    nm = get_notification_manager()
    # Acknowledge all currently unread
    for n in nm.notifications:
        n.acknowledged = True
    return {"ok": True, "message": "All notifications acknowledged"}

@app.post("/admin/system/process/stop")
async def stop_process():
    """Stop the Agent Runner process."""
    import sys
    import asyncio
    
    async def _exit():
        await asyncio.sleep(1)
        sys.exit(0)
    
    asyncio.create_task(_exit())
    logger.warning("Agent Runner process termination requested.")
    return {"ok": True, "message": "Agent Runner stopping in 1s..."}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 5460))
    # Run uvicorn programmatically
    uvicorn.run("agent_runner.main:app", host="0.0.0.0", port=port, reload=True)
