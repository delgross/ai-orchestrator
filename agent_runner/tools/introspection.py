
import logging
import os
import yaml
from typing import Dict, Any, List
from agent_runner.state import AgentState
from common.sovereign import get_sovereign_roles, get_sovereign_toggles

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
    Use this to answer questions about:
    - "What models are configured?"
    - "Inventory all LLMs"
    - "List all internal models"
    - "What model is the Router using?"
    - "What models are running?"
    Returns data from the database (source of truth), not from files.
    """
    try:
        # We fetch this from the Router's config API if available, 
        # or construct it from the Agent's local knowledge of the system state.
        
        # 1. Try fetching from Router Config API for truth
        base = state.gateway_base
        models = {}
        
        models = {}
        
        # Fetch keys from Registry
        roles = get_sovereign_roles()
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
    Reads the active configuration from Sovereign Memory (database), including all model assignments.
    Use this to answer questions about:
    - "What models are configured?"
    - "Inventory all LLMs"
    - "List all internal models"
    - "Show me the system configuration"
    IMPORTANT: Secrets are masked. Database is the source of truth - no disk reads.
    Returns all config keys including AGENT_MODEL, ROUTER_MODEL, VISION_MODEL, etc.
    """
    try:
        # Query configuration from database (config_state table)
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not initialized"}
        
        from agent_runner.db_utils import run_query
        query = "SELECT key, value FROM config_state"
        results = await run_query(state, query)
        
        if not results:
            return {"ok": False, "error": "No configuration found in database"}
        
        # Build config dictionary from database
        config_dict = {}
        for item in results:
            key = item.get("key")
            val = item.get("value")
            if key and val:
                # Parse JSON strings for readability
                if key in ["MODEL_INTELLIGENCE", "PERSONAS", "MCP_SERVERS", "PROVIDERS"] and isinstance(val, str):
                    try:
                        import json
                        config_dict[key] = json.loads(val)
                    except:
                        config_dict[key] = val
                # Mask secrets (keys containing API_KEY, SECRET, PASSWORD, TOKEN, PASS)
                elif any(secret_word in key.upper() for secret_word in ["API_KEY", "SECRET", "PASSWORD", "TOKEN", "PASS"]):
                    config_dict[key] = "***"
                else:
                    config_dict[key] = val
        
        env_vars = {
            "PORT": os.getenv("PORT"),
            "AGENT_FS_ROOT": str(state.agent_fs_root),
            "ROUTER_MODE": getattr(state, "router_mode", "unknown")
        }
        
        return {"ok": True, "config": config_dict, "env": env_vars, "source": "database"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_list_system_toggles(state: AgentState) -> Dict[str, Any]:
    """
    Returns a curated list of interactive system toggles and their current states.
    Use this to show the user what they can change.
    """
    try:
        toggles = []
        registry_toggles = get_sovereign_toggles()
        
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
                except Exception as e:
                    logger.debug(f"Failed to fetch router config: {e}")
            
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
