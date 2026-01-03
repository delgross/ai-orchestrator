
import logging
import os
import yaml
from typing import Dict, Any, List
from agent_runner.state import AgentState
from agent_runner.registry import SystemRegistry

logger = logging.getLogger("agent_runner.tools.introspection")

async def tool_get_service_status(state: AgentState) -> Dict[str, Any]:
    """
    Query the Orchestrator Router for a detailed health report of all services.
    Returns the status of Router, Agent, RAG, and SurrealDB.
    """
    try:
        base = state.gateway_base # e.g. http://127.0.0.1:5455
        url = f"{base}/admin/health/summary"
        
        client = await state.get_http_client()
        resp = await client.get(url, timeout=5.0)
        
        if resp.status_code != 200:
             return {"ok": False, "error": f"Router API returned {resp.status_code}"}
             
        data = resp.json()
        return {"ok": True, "status": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_get_component_map(state: AgentState) -> Dict[str, Any]:
    """
    Returns a map of all system roles (Agent, Router, Maître d', etc.) and their currently assigned models.
    Useful for answering "What model is the Router using?".
    """
    try:
        # We fetch this from the Router's config API if available, 
        # or construct it from the Agent's local knowledge of the system state.
        
        # 1. Try fetching from Router Config API for truth
        base = state.gateway_base
        models = {}
        
        # Fetch keys from Registry
        roles = SystemRegistry.get_all_roles()
        keys = [f"{r['id']}_model" for r in roles]
        
        client = await state.get_http_client()
        
        for key in keys:
            try:
                resp = await client.get(f"{base}/config/{key}", timeout=2.0)
                if resp.status_code == 200:
                    val = resp.json().get("value")
                    models[key] = val
            except Exception:
                models[key] = "unknown"

        # 2. Add local state overrides if needed
        # The AgentState object also has copies of these
        local_map = {
            "agent_model": state.agent_model,
            "router_model": getattr(state, "router_model", "unknown"), # Might not be on AgentState
            "fallback_model": state.fallback_model
        }
        
        return {
            "ok": True, 
            "remote_config": models, 
            "local_state": local_map,
            "description": "remote_config is the Source of Truth from the Database."
        }
    except Exception as e:
         return {"ok": False, "error": str(e)}

async def tool_get_active_configuration(state: AgentState) -> Dict[str, Any]:
    """
    Reads the active 'config.yaml' and relevant environment variables.
    IMPORTANT: Secrets are masked.
    """
    try:
        config_path = os.path.join(state.agent_fs_root, "config.yaml")
        if not os.path.exists(config_path):
             return {"ok": False, "error": "config.yaml not found"}
             
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)
            
        # Mask secrets
        if "surreal" in cfg:
            cfg["surreal"]["pass"] = "***"
        if "api_keys" in cfg:
            for k in cfg["api_keys"]:
                cfg["api_keys"][k] = "***"
                
        env_vars = {
            "PORT": os.getenv("PORT"),
            "AGENT_FS_ROOT": str(state.agent_fs_root),
            "ROUTER_MODE": getattr(state, "router_mode", "unknown")
        }
        
        return {"ok": True, "config_yaml": cfg, "env": env_vars}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_list_system_toggles(state: AgentState) -> Dict[str, Any]:
    """
    Returns a curated list of interactive system toggles and their current states.
    Use this to show the user what they can change.
    """
    try:
        toggles = []
        registry_toggles = SystemRegistry.get_all_toggles()
        
        for t in registry_toggles:
            current_val = "unknown"
            
            # Fetch specific logic based on key type
            if t["key"] == "router_mode":
                try:
                    base = state.gateway_base
                    client = await state.get_http_client()
                    resp = await client.get(f"{base}/config/router_mode", timeout=1.0)
                    if resp.status_code == 200:
                        current_val = resp.json().get("value", "unknown")
                except: pass
            
            elif t["key"] == "policy:internet":
                 current_val = "enabled" if state.internet_available else "local_only"
                 
            elif t["key"] == "policy:safety":
                 # Placeholder fetch
                 current_val = "moderate"
                 
            # Add to list
            toggles.append({
                "name": t["name"],
                "key": t["key"],
                "current_value": current_val,
                "options": t["options"],
                "description": t["description"]
            })
        
        # 4. Voice Mode (If applicable)
        # Maybe fetch from config
        
        return {
            "ok": True,
            "count": len(toggles),
            "toggles": toggles,
            "help": "Use set_system_config(key, val) or set_policy(key, val) to change these."
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
