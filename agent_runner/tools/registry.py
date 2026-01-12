import os
import logging
from typing import Dict, Any, List
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.registry")

async def tool_registry_list(state: AgentState) -> Dict[str, Any]:
    """List all files in the Permanent Registry from database (source of truth)."""
    try:
        # Database is the source of truth - read from DB, not disk
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not available"}
        
        await state.memory.ensure_connected()
        
        # Get all sovereign files from database
        sovereign_files = await state.memory.list_sovereign_files()
        
        # Extract kb_ids as file paths (add .md extension for compatibility)
        file_list = [f"{f.get('kb_id')}.md" for f in sovereign_files if f.get('kb_id')]
        
        return {"ok": True, "files": file_list}
    except Exception as e:
        logger.error(f"Registry list error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}

async def tool_registry_read(state: AgentState, filename: str) -> Dict[str, Any]:
    """Read a specific Registry file from database (source of truth)."""
    try:
        # Database is the source of truth - read from DB, not disk
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not available"}
        
        await state.memory.ensure_connected()
        
        # Remove .md extension if present to get kb_id
        kb_id = filename.replace(".md", "").strip()
        
        # Retrieve content from database
        content = await state.memory.get_sovereign_file_content(kb_id)
        
        if content is None:
            return {"ok": False, "error": f"File '{filename}' (kb_id: {kb_id}) does not exist in database."}
        
        return {"ok": True, "content": content}
    except Exception as e:
        logger.error(f"Registry read error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}

async def tool_registry_append(state: AgentState, filename: str, text: str) -> Dict[str, Any]:
    """Append text to a Registry file in database (source of truth)."""
    try:
        # Database is the source of truth - write to DB, then sync to disk if needed
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not available"}
        
        await state.memory.ensure_connected()
        
        # Remove .md extension if present to get kb_id
        kb_id = filename.replace(".md", "").strip()
        
        # Get existing content
        existing_content = await state.memory.get_sovereign_file_content(kb_id) or ""
        
        # Append new text
        entry = f"\n- {text}"
        new_content = existing_content + entry
        
        # Sync to database (this will wipe and replace)
        res = await state.memory.sync_sovereign_file(kb_id, new_content)
        
        if not res.get("ok"):
            return {"ok": False, "error": f"Failed to append to registry: {res.get('error', 'Unknown error')}"}
        
        # Invalidate cache
        if hasattr(state, "engine_ref") and state.engine_ref:
             if hasattr(state.engine_ref, "registry_cache"):
                 state.engine_ref.registry_cache = None

        return {"ok": True, "message": f"Appended to {filename} in database"}
    except Exception as e:
        logger.error(f"Registry append error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}

async def tool_registry_write(state: AgentState, filename: str, content: str) -> Dict[str, Any]:
    """Overwrite a Registry file completely in database (source of truth)."""
    try:
        # Database is the source of truth - write to DB, then sync to disk if needed
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not available"}
        
        await state.memory.ensure_connected()
        
        # Remove .md extension if present to get kb_id
        kb_id = filename.replace(".md", "").strip()
        
        # Sync to database (this will wipe and replace)
        res = await state.memory.sync_sovereign_file(kb_id, content)
        
        if not res.get("ok"):
            return {"ok": False, "error": f"Failed to write registry: {res.get('error', 'Unknown error')}"}
        
        # Invalidate cache
        if hasattr(state, "engine_ref") and state.engine_ref:
             if hasattr(state.engine_ref, "registry_cache"):
                 state.engine_ref.registry_cache = None
                 
        return {"ok": True, "message": f"Wrote {filename} to database"}
    except Exception as e:
        logger.error(f"Registry write error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}
