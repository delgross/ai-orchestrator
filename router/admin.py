import os
import json
import shutil
import time
import logging
from typing import Any, Optional
from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from router.config import state, VERSION
from router.providers import load_providers

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger("router.admin")

async def _proxy_agent_runner(method: str, path: str, json_body: Any = None):
    from router.config import AGENT_RUNNER_URL
    # Ensure path doesn't result in double /admin/admin
    clean_path = path if not path.startswith("/admin") else path[6:]
    if not clean_path.startswith("/"): clean_path = "/" + clean_path
    url = f"{AGENT_RUNNER_URL}/admin{clean_path}"
    try:
        if method == "GET":
            r = await state.client.get(url, timeout=10.0)
        elif method == "POST":
            r = await state.client.post(url, json=json_body, timeout=10.0)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
            
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to proxy to agent runner [{method} {url}]: {type(e).__name__}: {e}")
        # Return 502 but with JSON details if possible
        raise HTTPException(status_code=502, detail=f"Agent Runner unavailable: {str(e)}")

@router.get("/system-status")
async def system_status():
    """Aggregate status of all services (Router, Agent, Ollama)."""
    # 1. Router Self-Check
    router_status = {"ok": True, "version": VERSION}
    
    # 2. Agent Check (via Proxy)
    agent_data = {}
    try:
        # We use the raw client to avoid raising HTTP 502 logic in _proxy wrapper if down
        # But _proxy_agent_runner handles generic logic. Let's try/except it.
        agent_data = await _proxy_agent_runner("GET", "/system-status")
    except Exception as e:
        logger.warning(f"Status check: Agent unreachable: {e}")
        agent_data = {"ok": False, "mode": "Offline", "internet": "Unknown", "ollama_ok": False}

    # 3. Construct Unified Response (The 'Defined Channel' Contract)
    return {
        "ok": True,
        "services": {
            "router": router_status,
            "agent_runner": {"ok": agent_data.get("ok", False)}
        },
        "ollama_ok": agent_data.get("ollama_ok", False),
        "database_ok": agent_data.get("database_ok", False),
        "internet": agent_data.get("internet", "Unknown"),
        "mode": agent_data.get("mode", "Production"),
        # Pass through Agent capabilities
        "hardware_verified": agent_data.get("hardware_verified", False),
        "limits": agent_data.get("limits", {})
    }

@router.get("/health/summary")
async def health_summary():
    """Aggregate all health indicators for the Dashboard Health Sentinel."""
    # 1. Get Circuit Breakers (Router + Agent)
    router_breakers = state.circuit_breakers.get_status()
    agent_breakers = {}
    try:
        agent_cb_data = await _proxy_agent_runner("GET", "/circuit-breaker/status")
        agent_breakers = agent_cb_data.get("breakers", {})
    except: pass
    
    all_breakers = {**router_breakers, **agent_breakers}
    
    # 2. Get Recent Anomalies
    anomalies = []
    try:
        from common.observability import get_observability
        obs = get_observability()
        anomalies_data = await obs.get_anomalies(limit=5)
        anomalies = anomalies_data.get("anomalies", [])
    except: pass
    
    # 3. Check for any 'OPEN' breakers (Critical Degradation)
    open_breakers = [b for b in all_breakers.values() if b.get("state") == "open"]
    
    # 4. Construct Summary
    return {
        "ok": True,
        "timestamp": time.time(),
        "status": "degraded" if open_breakers or anomalies else "healthy",
        "critical_count": len(open_breakers),
        "warning_count": len(anomalies),
        "open_breakers": open_breakers,
        "anomalies": anomalies,
        "latest_anomaly": anomalies[0] if anomalies else None,
        "overall_status": all_breakers  # Full dump for UI to parse if needed
    }


@router.get("/background-tasks")
async def proxy_background_tasks():
    return await _proxy_agent_runner("GET", "/background-tasks")

@router.post("/reload-mcp")
async def proxy_reload_mcp():
    return await _proxy_agent_runner("POST", "/reload-mcp")

@router.get("/system-prompt")
async def proxy_system_prompt():
    return await _proxy_agent_runner("GET", "/system-prompt")

@router.get("/memory/facts")
async def proxy_memory_facts(query: str = "", limit: int = 100):
    # Pass query params manually if needed, simplified here
    path = f"/memory/facts?query={query}&limit={limit}"
    return await _proxy_agent_runner("GET", path)

@router.post("/mcp/toggle")
async def proxy_mcp_toggle(request: Request):
    body = await request.json()
    return await _proxy_agent_runner("POST", "/mcp/toggle", body)

@router.post("/mcp/upload-config")
async def proxy_mcp_upload_config(raw_text: str = Form(...)):
    """Proxy MCP config upload to Agent Runner."""
    from router.config import AGENT_RUNNER_URL
    try:
        # We must forward as form data
        # Using state.client.post with 'data' argument sends form-urlencoded
        r = await state.client.post(
            f"{AGENT_RUNNER_URL}/admin/mcp/upload-config", 
            data={"raw_text": raw_text},
            timeout=30.0
        )
        return JSONResponse(r.json(), status_code=r.status_code)
    except Exception as e:
        logger.error(f"Failed to proxy MCP upload: {e}")
        return {"ok": False, "error": str(e)} 

@router.post("/mcp/upload-config-json")
async def proxy_mcp_upload_json(request: Request):
    """Proxy JSON payload to Agent Runner's new JSON-compatible endpoint."""
    body = await request.json()
    return await _proxy_agent_runner("POST", "/mcp/upload-config-json", body)

@router.get("/mcp/server/status")
async def proxy_mcp_server_status():
    """Proxy MCP server status request to Agent Runner."""
    return await _proxy_agent_runner("GET", "/admin/mcp/server/status")

@router.post("/ingestion/resume")
async def resume_ingestion():
    """Resume a paused ingestion pipeline."""
    return await _proxy_agent_runner("POST", "/ingestion/resume")

@router.post("/ingestion/pause")
async def pause_ingestion():
    """Manually pause the ingestion pipeline."""
    return await _proxy_agent_runner("POST", "/ingestion/pause")

@router.post("/ingestion/clear-and-resume")
async def proxy_ingestion_clear():
    return await _proxy_agent_runner("POST", "/ingestion/clear-and-resume")

@router.get("/ingestion/status")
async def proxy_ingestion_status():
    return await _proxy_agent_runner("GET", "/ingestion/status")

@router.get("/memory/status")
async def proxy_memory_status():
    return await _proxy_agent_runner("GET", "/memory/status")

@router.get("/circuit-breaker/status")
async def proxy_cb_status():
    """Correctly aggregated status for all services (Router + Agent)."""
    router_breakers = state.circuit_breakers.get_status()
    agent_breakers = {}
    try:
        # Fetch from agent (which returns {"breakers": {...}, ...})
        data = await _proxy_agent_runner("GET", "/circuit-breaker/status")
        agent_breakers = data.get("breakers", {})
    except: pass
    
    return {"ok": True, "breakers": {**router_breakers, **agent_breakers}}

# Dashboard Tracking Proxies
@router.get("/dashboard/insights")
async def proxy_dash_insights():
    return await _proxy_agent_runner("GET", "/dashboard/insights")

@router.get("/mcp/tools")
async def proxy_mcp_tools(server: Optional[str] = None):
    path = "/mcp/tools"
    if server:
        path += f"?server={server}"
    return await _proxy_agent_runner("GET", path)

@router.post("/dashboard/track/error")
async def proxy_dash_error(request: Request):
    body = await request.json()
    return await _proxy_agent_runner("POST", "/dashboard/track/error", body)

@router.post("/dashboard/track/interaction")
async def proxy_dash_interaction(request: Request):
    body = await request.json()
    return await _proxy_agent_runner("POST", "/dashboard/track/interaction", body)

@router.post("/reload")
async def reload_config():
    """Reload providers and system state."""
    state.providers = load_providers()
    state.models_cache = (0.0, {}) # Clear cache
    return {"ok": True, "message": "Configuration reloaded", "providers": list(state.providers.keys())}

@router.get("/active-model")
async def get_active_model():
    """Return the default or active model configuration."""
    return {
        "ok": True,
        "ollama_num_ctx": state.ollama_num_ctx,
        "mcp_access": state.mcp_tool_access_enabled
    }

@router.post("/mcp-toggle")
async def toggle_mcp(enabled: bool):
    """Enable or disable MCP tool access globally at the router level."""
    state.mcp_tool_access_enabled = enabled
    return {"ok": True, "enabled": enabled}

@router.post("/telemetry/log")
async def proxy_telemetry_log(request: Request):
    body = await request.json()
    return await _proxy_agent_runner("POST", "/telemetry/log", body)

@router.get("/observability/trace")
async def get_request_traces(limit: int = 50):
    """Return recent request traces (Request Lifecycle)."""
    try:
        from common.observability import get_observability
        from dataclasses import asdict
        obs = get_observability()
        # Get recent completed requests
        requests = [asdict(r) for r in list(obs.completed_requests)[-limit:]]
        # Reverse to show newest first
        return {"ok": True, "traces": requests[::-1]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/observability/stuck")
async def get_stuck_requests_endpoint(timeout: float = 30.0):
    """Return currently stuck requests."""
    try:
        from common.observability import get_observability
        obs = get_observability()
        stuck = await obs.get_stuck_requests(timeout_seconds=timeout)
        return {"ok": True, "stuck_requests": stuck}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/observability/anomalies/{anomaly_id}/ack")
async def acknowledge_anomaly_endpoint(anomaly_id: str):
    """Acknowledge an anomaly."""
    from common.observability import get_observability
    obs = get_observability()
    success = obs.acknowledge_anomaly(anomaly_id)
    return {"ok": success}

@router.post("/observability/reexamine")
async def reexamine_observability(request: Request):
    """
    Force re-examination/reset of observability metrics.
    Body: {"targets": ["traces", "counters", ...]} (Optional, defaults to all)
    """
    try:
        from common.observability import get_observability
        body = await request.json()
        targets = body.get("targets", ["all"])
        
        obs = get_observability()
        await obs.reset_history(targets)
        
        return {"ok": True, "message": f"Reset targets: {targets}"}
    except Exception as e:
        logger.error(f"Re-examine failed: {e}")
        return {"ok": False, "error": str(e)}

@router.get("/observability/anomalies")
async def get_anomalies(limit: int = 50):
    """Return recently detected system anomalies."""
    try:
        from common.observability import get_observability
        obs = get_observability()
        # Also try to get from agent runner if local obs is empty
        local_data = await obs.get_anomalies(limit=limit)
        
        # Merge or prioritize agent anomalies (since agent does heavy lifting)
        # For simplicity, let's just use local for now, but in future perform merge
        return local_data
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/observability/clear")
async def clear_anomalies_proxy():
    """Clear anomalies in both router and agent."""
    try:
        # Clear local
        from common.observability import get_observability
        obs = get_observability()
        obs.clear_anomalies()
        
        # Clear agent
        await _proxy_agent_runner("POST", "/admin/observability/clear")
        
        return {"ok": True, "message": "Anomalies cleared system-wide"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/observability/stats")
async def get_observability_stats():
    """Return detailed system performance and health metrics."""
    try:
        from common.observability import get_observability
        from dataclasses import asdict
        obs = get_observability()
        metrics = await obs.get_system_metrics()
        return {"ok": True, "metrics": asdict(metrics)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/health-full")
async def full_health():
    """Detailed health check including all provider connectivity."""
    results = {}
    for name, prov in state.providers.items():
        try:
            r = await state.client.get(f"{prov.base_url}/health", timeout=2.0)
            results[name] = r.status_code == 200
        except:
            results[name] = False
    return {"ok": True, "providers": results}

@router.get("/circuit-breakers")
async def get_circuit_breakers():
    """Return the status of all circuit breakers in the router."""
    return {"ok": True, "breakers": state.circuit_breakers.get_status()}

@router.post("/circuit-breakers/{name}/reset")
@router.post("/circuit-breaker/reset/{name}")
async def reset_circuit_breaker(name: str):
    """Manually reset a specific circuit breaker (Router + Agent)."""
    state.circuit_breakers.reset(name)
    # Also attempt to reset in Agent
    try:
        await _proxy_agent_runner("POST", f"/circuit-breaker/reset/{name}")
    except:
        pass
    return {"ok": True, "message": f"Circuit breaker '{name}' reset"}

@router.post("/circuit-breakers/reset-all")
async def reset_all_circuit_breakers():
    """Manually reset all circuit breakers."""
    """Manually reset all circuit breakers (Router + Agent)."""
    state.circuit_breakers.reset_all()
    # Also reset Agent breakers
    try:
        await _proxy_agent_runner("POST", "/circuit-breaker/reset-all")
    except:
        pass

@router.get("/llm/roles")
async def proxy_get_roles():
    return await _proxy_agent_runner("GET", "/llm/roles")

@router.post("/llm/roles")
async def proxy_set_roles(request: Request):
    body = await request.json()
    return await _proxy_agent_runner("POST", "/llm/roles", body)


# Config File Management (New)
@router.get("/config/files")
async def list_config_files():
    """List available configuration files."""
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = {
        "providers.yaml": os.path.join(root_dir, "providers.yaml"),
        "config.yaml": os.path.join(root_dir, "config/config.yaml"),
        ".env": os.path.join(root_dir, ".env"),
    }
    
    return {
        "ok": True, 
        "files": [{"name": k, "path": v, "exists": os.path.exists(v)} for k, v in files.items()]
    }

@router.get("/config/read")
async def read_config_file(path: str):
    """Read content of a config file."""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"ok": True, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/write")
async def write_config_file(request: Request):
    """Write content to a config file."""
    body = await request.json()
    path = body.get("path")
    content = body.get("content")
    
    if not path or content is None:
        raise HTTPException(status_code=400, detail="Missing path or content")
        
    try:
        # Create backup
        if os.path.exists(path):
            shutil.copy2(path, f"{path}.bak.{int(time.time())}")
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"ok": True, "message": "File saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from router.providers import provider_headers

@router.get("/llm/status")
async def get_llm_status():
    """Get detailed status of all LLM providers."""
    from router.config import OLLAMA_BASE
    
    status = []
    
    # Check Ollama
    ollama_ok = False
    ollama_models = []
    try:
        r = await state.client.get(f"{OLLAMA_BASE}/api/tags", timeout=2.0)
        if r.status_code == 200:
            ollama_ok = True
            ollama_models = [m.get("name") for m in r.json().get("models", [])]
    except: pass
    
    status.append({
        "id": "ollama",
        "name": "Ollama (Local)",
        "type": "local",
        "status": "online" if ollama_ok else "offline",
        "models": ollama_models,
        "base_url": OLLAMA_BASE
    })
    
    # Check Providers
    for name, prov in state.providers.items():
        prov_ok = False
        prov_models = ["*"]
        try:
            # Use the provider's specific models path if available, or default to /models
            path = getattr(prov, "models_path", "/models")
            url = f"{prov.base_url.rstrip('/')}{path}"
            
            # Use proper headers (Auth token)
            headers = provider_headers(prov)
            
            r = await state.client.get(url, headers=headers, timeout=3.0)
            prov_ok = r.status_code < 400
            
            if r.status_code == 200:
                data = r.json()
                if "data" in data and isinstance(data["data"], list):
                    fetched_models = [m.get("id") for m in data["data"] if isinstance(m, dict) and "id" in m]
                    # Filter for only chat models if possible? No, listing all is safer for now.
                    if fetched_models:
                        prov_models = sorted(fetched_models)
        except Exception as e:
            logger.warning(f"Failed to list models for {name}: {e}")
            pass
        
        status.append({
            "id": name,
            "name": f"Provider: {name}",
            "type": "cloud",
            "status": "online" if prov_ok else "offline",
            "models": prov_models,
            "base_url": prov.base_url
        })
        
    return {"ok": True, "llms": status}

@router.get("/llm/roles")
async def get_llm_roles_proxy():
    """Proxy request to agent runner to get roles."""
    from router.config import AGENT_RUNNER_URL
    try:
        r = await state.client.get(f"{AGENT_RUNNER_URL}/admin/roles")
        return JSONResponse(r.json(), status_code=r.status_code)
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/llm/roles")
async def update_llm_roles_proxy(request: Request):
    """Proxy update request to agent runner."""
    from router.config import AGENT_RUNNER_URL
    try:
        body = await request.json()
        r = await state.client.post(f"{AGENT_RUNNER_URL}/admin/roles", json=body)
        return JSONResponse(r.json(), status_code=r.status_code)
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.post("/llm/ollama/active")
async def set_active_ollama_model(model: str):
    """Update the active Ollama model in runtime state."""
    # Note: In a persistent system, we'd write this to config too.
    # For now, we update the runtime state used by logic.
    state.system_router_model = model
    return {"ok": True, "message": f"Active Ollama model set to {model}"}

@router.post("/llm/embedding/default")
async def set_default_embedding_model(model: str):
    """Update the default embedding model in runtime state."""
    state.default_embedding_model = model
    return {"ok": True, "message": f"Default embedding model set to {model}"}


@router.get("/docs/list")
async def proxy_docs_list():
    return await _proxy_agent_runner("GET", "/docs/list")

@router.get("/docs/read")
async def proxy_docs_read(path: str):
    import urllib.parse
    encoded_path = urllib.parse.quote(path)
    return await _proxy_agent_runner("GET", f"/docs/read?path={encoded_path}")

@router.get("/notifications")
async def proxy_notifications(priority: Optional[str] = None, unread: bool = False, limit: int = 50):
    path = f"/notifications?unread={str(unread).lower()}&limit={limit}"
    if priority:
        path += f"&priority={priority}"
    return await _proxy_agent_runner("GET", path)

@router.post("/notifications/acknowledge")
async def proxy_ack_notifications():
    return await _proxy_agent_runner("POST", "/notifications/acknowledge")

# --- Process Control ---

@router.post("/system/process/router/stop")
async def stop_router():
    """Stop the Router process."""
    import sys
    # Schedule exit
    import asyncio
    async def _exit():
        await asyncio.sleep(1)
        sys.exit(0)
    asyncio.create_task(_exit())
    return {"ok": True, "message": "Router stopping in 1s..."}

@router.post("/system/restart")
async def restart_system():
    """Trigger a full system restart (Agent + Router)."""
    # Verify Restart Script Exists
    import os
    import subprocess
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(root_dir, "bin", "restart_all.sh")
    
    # If script doesn't exist, try local logic
    if not os.path.exists(script_path):
         # Try at least to restart agent, then self
         await restart_agent_runner()
         await restart_router()
         return {"ok": True, "message": "Triggered sequential restart sequence"}

    try:
        # Spawn detached process
        subprocess.Popen([script_path], cwd=os.path.dirname(script_path), start_new_session=True)
        return {"ok": True, "message": "System restart triggered via script"}
    except Exception as e:
        return {"ok": False, "error": f"Failed to trigger restart script: {e}"}

@router.post("/system/process/router/restart")
async def restart_router():
    """Restart the Router process using os.execv."""
    import sys
    import os
    import asyncio
    
    async def _restart():
        await asyncio.sleep(1)
        # Re-execute the current process
        python = sys.executable
        os.execv(python, [python] + sys.argv)
        
    asyncio.create_task(_restart())
    return {"ok": True, "message": "Router restarting in 1s..."}

@router.post("/system/process/agent/start")
async def start_agent_runner():
    """Start the Agent Runner process if not running."""
    import subprocess
    import sys
    
    # Check if running (simplified check via health proxy)
    try:
        await _proxy_agent_runner("GET", "/")
        return {"ok": False, "message": "Agent Runner is already running"}
    except:
        pass # Not running or unreachable

    # Spawn
    # We assume standard location: module agent_runner.main
    # We need to run it as a detached process or background
    cmd = [sys.executable, "-m", "uvicorn", "agent_runner.main:app", "--host", "127.0.0.1", "--port", "5460"]
    
    try:
        subprocess.Popen(cmd, cwd=os.getcwd(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"ok": True, "message": "Agent Runner started"}
    except Exception as e:
        return {"ok": False, "message": f"Failed to start Agent Runner: {e}"}

@router.post("/system/process/agent/stop")
async def stop_agent_runner():
    """Stop the Agent Runner process."""
    # Proxy to agent runner's own stop endpoint
    return await _proxy_agent_runner("POST", "/system/process/stop")


@router.post("/system/process/agent/restart")
async def restart_agent_runner():
    """Restart the Agent Runner process (Stop -> Start)."""
    import asyncio
    
    # 1. Stop
    try:
        await _proxy_agent_runner("POST", "/system/process/stop")
    except:
        pass # Might be down already
        
    # 2. Wait
    await asyncio.sleep(2.0)
    
    return await start_agent_runner()

@router.get("/budget")
async def get_budget():
    """Return current budget status."""
    from common.budget import get_budget_tracker
    b = get_budget_tracker()
    # Force reload to get latest file changes
    b._load()
    return {
        "ok": True,
        "current_spend": b.current_spend,
        "daily_limit_usd": b.daily_limit_usd,
        "last_reset": b.last_reset,
        "percent_used": (b.current_spend / max(0.01, b.daily_limit_usd)) * 100
    }

@router.post("/budget/reset")
async def reset_budget():
    """Reset the current budget spend."""
    from common.budget import get_budget_tracker
    b = get_budget_tracker()
    b.reset()
    return {"ok": True, "message": "Budget reset successfully."}

@router.get("/config/yaml")
async def get_config_yaml():
    """Read config.yaml content."""
    import os
    # Assuming CONFIG_FILE is global or we find it
    config_path = os.path.expanduser("~/Sync/Antigravity/ai/config/config.yaml") 
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return {"ok": True, "content": f.read()}
    return {"ok": False, "error": "File not found"}

@router.get("/logs/tail")
async def tail_log(lines: int = 10, service: str = "agent_runner"):
    """Tail the last N lines of a service log file."""
    import os
    if service not in ["agent_runner", "router", "ollama"]:
         return {"ok": False, "error": "Invalid service name"}
          
    # Try finding logs in standard locations
    paths = [
        f"logs/{service}.log",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", f"{service}.log")
    ]
    
    log_file = None
    for p in paths:
        if os.path.exists(p):
            log_file = p
            break
            
    if not log_file:
        return {"ok": False, "lines": ["Log file not found"]}
        
    try:
        file_size = os.path.getsize(log_file)
        read_size = min(file_size, lines * 500) # heuristic: 500 chars per line?
        
        with open(log_file, "rb") as f:
            if file_size > read_size:
                f.seek(file_size - read_size)
            data = f.read()
            
        text = data.decode('utf-8', errors='replace')
        all_lines = text.splitlines()
        return {"ok": True, "logs": all_lines[-lines:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@router.get("/logs/cloud_uplink")
async def get_cloud_uplink_logs(lines: int = 15):
    """Specific endpoint for H100 Uplink logs."""
    import os
    # Assuming 'logs' dir at root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(root_dir, "logs", "cloud_uplink.log")
    
    if not os.path.exists(log_path):
        return {"ok": True, "logs": ["> Awaiting H100 Uplink connection...", "> System Ready."]}
        
    try:
        file_size = os.path.getsize(log_path)
        read_size = min(file_size, lines * 200) 
        
        with open(log_path, "rb") as f:
            if file_size > read_size:
                f.seek(file_size - read_size)
            data = f.read()
            
        text = data.decode('utf-8', errors='replace')
        return {"ok": True, "logs": text.splitlines()[-lines:]}
    except Exception as e:
        return {"ok": False, "logs": [f"> Error reading uplink: {e}"]}

@router.get("/dashboard/state")
async def get_dashboard_state():
    """Aggregated state for the V2 Dashboard to minimize polling."""
    import asyncio
    
    # 1. Gather all data in parallel
    try:
        [status, summary, metrics, budget, llms, ingestion, memory_stats] = await asyncio.gather(
            system_status(),
            health_summary(),
            get_observability_stats(),
            get_budget(),
            get_llm_status(),
            proxy_ingestion_status(),
            proxy_memory_status(),
            return_exceptions=True
        )
        
        return {
            "ok": True,
            "timestamp": time.time(),
            "status": status if not isinstance(status, Exception) else {"error": str(status)},
            "summary": summary if not isinstance(summary, Exception) else {"error": str(summary)},
            "metrics": metrics if not isinstance(metrics, Exception) else {"error": str(metrics)},
            "budget": budget if not isinstance(budget, Exception) else {"error": str(budget)},
            "llms": llms if not isinstance(llms, Exception) else {"error": str(llms)},
            "ingestion": ingestion if not isinstance(ingestion, Exception) else {"error": str(ingestion)},
            "memory_stats": memory_stats if not isinstance(memory_stats, Exception) else {"error": str(memory_stats)}
        }
    except Exception as e:
        logger.error(f"Dashboard state aggregation failed: {e}")
        return {"ok": False, "error": str(e)}

@router.get("/logs/stream")
async def stream_logs(request: Request, services: str = "agent_runner,router"):
    """SSE endpoint for real-time log streaming."""
    from fastapi.responses import StreamingResponse
    import asyncio
    
    service_list = [s.strip() for s in services.split(",")]
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    async def log_generator():
        # Track file positions for each service
        positions = {}
        log_paths = {}
        
        for s in service_list:
            p = os.path.join(root_dir, "logs", f"{s}.log")
            if os.path.exists(p):
                log_paths[s] = p
                # Start at the end of the file
                positions[s] = os.path.getsize(p)
        
        while True:
            if await request.is_disconnected():
                break
                
            for s, path in log_paths.items():
                try:
                    current_size = os.path.getsize(path)
                    if current_size > positions[s]:
                        with open(path, "r", encoding="utf-8", errors="replace") as f:
                            f.seek(positions[s])
                            lines = f.readlines()
                            positions[s] = f.tell()
                            
                            for line in lines:
                                if line.strip():
                                    data = json.dumps({"service": s, "line": line.strip()})
                                    yield f"data: {data}\n\n"
                except Exception as e:
                    logger.error(f"Error streaming logs for {s}: {e}")
                    
            await asyncio.sleep(0.5) # Poll files every 500ms
            
    return StreamingResponse(log_generator(), media_type="text/event-stream")
