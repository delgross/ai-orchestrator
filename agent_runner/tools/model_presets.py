"""
Model Preset Management Tools

Allows saving, loading, listing, and deleting named model configurations.
"""

import logging
from typing import Dict, Any, List, Optional
from agent_runner.db_utils import run_query
from agent_runner.state import AgentState
from agent_runner.constants import MODEL_ROLES

logger = logging.getLogger("agent_runner")

async def tool_save_model_preset(
    state: AgentState,
    name: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Save the current model configuration as a named preset.
    
    Args:
        state: AgentState instance
        name: Unique name for the preset (e.g., "production", "development", "high-performance")
        description: Optional description of the preset
    
    Returns:
        Dict with success status and preset details
    """
    if not state.memory or not state.memory.initialized:
        return {
            "ok": False,
            "error": "Memory server not initialized"
        }
    
    # Collect current model configuration
    current_models = {}
    for role in MODEL_ROLES:
        model = getattr(state, role, None)
        if model:
            current_models[role] = model
    
    if not current_models:
        return {
            "ok": False,
            "error": "No models configured to save"
        }
    
    try:
        # Check if preset already exists
        check_query = "SELECT * FROM model_preset WHERE name = $name"
        existing = await run_query(state, check_query, {"name": name})
        
        if existing and len(existing) > 0:
            # Update existing preset
            query = """
            UPDATE model_preset SET
                models = $models,
                description = $description,
                updated_at = time::now()
            WHERE name = $name;
            """
            await run_query(state, query, {
                "name": name,
                "models": current_models,
                "description": description or ""
            })
            action = "updated"
        else:
            # Create new preset
            query = """
            CREATE model_preset SET
                name = $name,
                models = $models,
                description = $description,
                created_at = time::now(),
                updated_at = time::now(),
                created_by = 'system';
            """
            await run_query(state, query, {
                "name": name,
                "models": current_models,
                "description": description or ""
            })
            action = "created"
        
        logger.info(f"Model preset '{name}' {action} with {len(current_models)} models")
        
        return {
            "ok": True,
            "action": action,
            "preset": {
                "name": name,
                "description": description,
                "models": current_models,
                "model_count": len(current_models)
            }
        }
    except Exception as e:
        logger.error(f"Failed to save model preset '{name}': {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e)
        }


async def tool_load_model_preset(
    state: AgentState,
    name: str
) -> Dict[str, Any]:
    """
    Load a named model preset and apply it to all model roles.
    
    Args:
        state: AgentState instance
        name: Name of the preset to load
    
    Returns:
        Dict with success status and applied configuration
    """
    if not state.memory or not state.memory.initialized:
        return {
            "ok": False,
            "error": "Memory server not initialized"
        }
    
    try:
        # Fetch preset from database
        query = "SELECT * FROM model_preset WHERE name = $name"
        result = await run_query(state, query, {"name": name})
        
        if not result or len(result) == 0:
            return {
                "ok": False,
                "error": f"Preset '{name}' not found"
            }
        
        preset = result[0]
        models = preset.get("models", {})
        
        if not models:
            return {
                "ok": False,
                "error": f"Preset '{name}' has no model configuration"
            }
        
        # Apply models to state via config_manager
        applied = {}
        failed = []
        
        # Map role names to config keys
        role_to_key = {
            "agent_model": "AGENT_MODEL",
            "router_model": "ROUTER_MODEL",
            "task_model": "TASK_MODEL",
            "summarization_model": "SUMMARIZATION_MODEL",
            "vision_model": "VISION_MODEL",
            "mcp_model": "MCP_MODEL",
            "finalizer_model": "FINALIZER_MODEL",
            "fallback_model": "FALLBACK_MODEL",
            "intent_model": "INTENT_MODEL",
            "pruner_model": "PRUNER_MODEL",
            "healer_model": "HEALER_MODEL",
            "critic_model": "CRITIC_MODEL",
            "embedding_model": "EMBEDDING_MODEL",
        }
        
        for role in MODEL_ROLES:
            if role in models:
                model_value = models[role]
                config_key = role_to_key.get(role)
                
                if not config_key:
                    logger.warning(f"No config key mapping for role: {role}")
                    failed.append(role)
                    continue
                
                try:
                    success = await state.config_manager.set_config_value(config_key, model_value)
                    if success:
                        applied[role] = model_value
                    else:
                        failed.append(role)
                except Exception as e:
                    logger.error(f"Failed to apply {role} = {model_value}: {e}")
                    failed.append(role)
        
        if failed:
            return {
                "ok": False,
                "error": f"Failed to apply models for: {', '.join(failed)}",
                "applied": applied,
                "failed": failed
            }
        
        logger.info(f"Loaded model preset '{name}': {len(applied)} models applied")
        
        return {
            "ok": True,
            "preset_name": name,
            "applied_models": applied,
            "model_count": len(applied)
        }
    except Exception as e:
        logger.error(f"Failed to load model preset '{name}': {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e)
        }


async def tool_list_model_presets(
    state: AgentState
) -> Dict[str, Any]:
    """
    List all available model presets.
    
    Args:
        state: AgentState instance
    
    Returns:
        Dict with list of presets and their details
    """
    if not state.memory or not state.memory.initialized:
        return {
            "ok": False,
            "error": "Memory server not initialized"
        }
    
    try:
        query = "SELECT name, description, models, created_at, updated_at FROM model_preset ORDER BY name"
        result = await run_query(state, query)
        
        if not result:
            return {
                "ok": True,
                "presets": [],
                "count": 0
            }
        
        presets = []
        for row in result:
            presets.append({
                "name": row.get("name", "Unknown"),
                "description": row.get("description", ""),
                "model_count": len(row.get("models", {})),
                "created_at": str(row.get("created_at", "")),
                "updated_at": str(row.get("updated_at", ""))
            })
        
        return {
            "ok": True,
            "presets": presets,
            "count": len(presets)
        }
    except Exception as e:
        logger.error(f"Failed to list model presets: {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e)
        }


async def tool_delete_model_preset(
    state: AgentState,
    name: str
) -> Dict[str, Any]:
    """
    Delete a named model preset.
    
    Args:
        state: AgentState instance
        name: Name of the preset to delete
    
    Returns:
        Dict with success status
    """
    if not state.memory or not state.memory.initialized:
        return {
            "ok": False,
            "error": "Memory server not initialized"
        }
    
    try:
        # Check if preset exists
        check_query = "SELECT * FROM model_preset WHERE name = $name"
        existing = await run_query(state, check_query, {"name": name})
        
        if not existing or len(existing) == 0:
            return {
                "ok": False,
                "error": f"Preset '{name}' not found"
            }
        
        # Delete preset
        query = "DELETE model_preset WHERE name = $name"
        await run_query(state, query, {"name": name})
        
        logger.info(f"Deleted model preset '{name}'")
        
        return {
            "ok": True,
            "deleted": name
        }
    except Exception as e:
        logger.error(f"Failed to delete model preset '{name}': {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e)
        }


async def tool_get_model_preset(
    state: AgentState,
    name: str
) -> Dict[str, Any]:
    """
    Get details of a specific model preset without loading it.
    
    Args:
        state: AgentState instance
        name: Name of the preset to retrieve
    
    Returns:
        Dict with preset details including all model assignments
    """
    if not state.memory or not state.memory.initialized:
        return {
            "ok": False,
            "error": "Memory server not initialized"
        }
    
    try:
        query = "SELECT * FROM model_preset WHERE name = $name"
        result = await run_query(state, query, {"name": name})
        
        if not result or len(result) == 0:
            return {
                "ok": False,
                "error": f"Preset '{name}' not found"
            }
        
        preset = result[0]
        models = preset.get("models", {})
        
        return {
            "ok": True,
            "preset": {
                "name": preset.get("name"),
                "description": preset.get("description", ""),
                "models": models,
                "model_count": len(models),
                "created_at": str(preset.get("created_at", "")),
                "updated_at": str(preset.get("updated_at", ""))
            }
        }
    except Exception as e:
        logger.error(f"Failed to get model preset '{name}': {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e)
        }

