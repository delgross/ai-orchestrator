
import logging
from typing import Dict, Any, Optional, List
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

logger = logging.getLogger("agent_runner.tools.registry")

async def tool_registry_manage(state: AgentState, action: str, target: str = None, value: Any = None) -> Dict[str, Any]:
    """
    Manage the Sovereign Registry (Database-Backed Configuration).
    
    Args:
        action: "list", "get", or "set".
        target: The target key or section.
                - For 'list': "models", "ports", "policies", "mcp".
                - For 'get'/'set': "{section}:{key}" (e.g., "policy:internet", "models:router").
        value: The value to set (only for 'set' action).
    """
    
    # Map sections to tables
    TABLE_MAP = {
        "models": "registry_models",
        "ports": "registry_ports",
        "policies": "registry_policies",
        "mcp": "registry_mcp",
        # Aliases
        "model": "registry_models",
        "port": "registry_ports",
        "policy": "registry_policies"
    }
    
    try:
        if action == "list":
            if not target:
                return {"ok": False, "error": "Missing target section (models, ports, policies, mcp)."}
            
            table = TABLE_MAP.get(target.lower())
            if not table:
                return {"ok": False, "error": f"Unknown section '{target}'. Valid: models, ports, policies, mcp."}
                
            # SELECT * FROM table
            q = f"SELECT * FROM {table} ORDER BY key ASC;"
            results = await run_query(state, q, {})
            
            # Format for readability
            formatted = {}
            for r in results:
                formatted[r['key']] = r['value']
            
            return {
                "ok": True, 
                "section": target,
                "data": formatted,
                "count": len(results),
                "message": f"Listing {len(results)} items in {target}."
            }

        elif action == "get":
            if not target or ":" not in target:
                 return {"ok": False, "error": "Target must be in format 'section:key' (e.g. policy:internet)."}
            
            section, key = target.split(":", 1)
            table = TABLE_MAP.get(section.lower())
            if not table:
                return {"ok": False, "error": f"Unknown section '{section}'."}

            q = f"SELECT * FROM {table} WHERE key = $key;"
            results = await run_query(state, q, {"key": key})
            
            if not results:
                return {"ok": False, "error": f"Key '{key}' not found in {section}."}
            
            item = results[0]
            return {
                "ok": True,
                "key": key,
                "value": item['value'],
                "source": item.get('source', 'unknown'),
                "last_updated": item.get('last_updated')
            }

        elif action == "set":
            if not target or ":" not in target:
                 return {"ok": False, "error": "Target must be in format 'section:key'."}
            if value is None:
                return {"ok": False, "error": "Missing 'value' for set action."}

            section, key = target.split(":", 1)
            table = TABLE_MAP.get(section.lower())
            if not table:
                return {"ok": False, "error": f"Unknown section '{section}'."}

            # UPSERT to ensure we capture the override
            # We explicitly mark source as 'runtime_override' (or 'agent_tool') to distinguish from sovereign.yaml
            q = f"""
            UPSERT type::thing($table, $key) 
            SET key = $key, value = $val, source = 'agent_tool', last_updated = time::now();
            """
            await run_query(state, q, {"table": table, "key": key, "val": value})
            
            return {
                "ok": True, 
                "message": f"Successfully updated {target} to '{value}'.",
                "persisted": True
            }
        
        else:
            return {"ok": False, "error": f"Unknown action '{action}'. Valid: list, get, set."}

    except Exception as e:
        logger.error(f"Registry Tool Error: {e}")
        return {"ok": False, "error": str(e)}
