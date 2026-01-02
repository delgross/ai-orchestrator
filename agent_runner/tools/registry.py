import os
import logging
from typing import Dict, Any, List
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.registry")

async def tool_registry_list(state: AgentState) -> Dict[str, Any]:
    """List all files in the Permanent Registry (Recursive)."""
    try:
        registry_dir = os.path.join(state.agent_fs_root, "data", "permanent")
        if not os.path.exists(registry_dir):
            return {"ok": True, "files": []}
        
        file_list = []
        for root, dirs, files in os.walk(registry_dir):
            for file in files:
                if file.endswith(".md") or file.endswith(".json"):
                    # Return relative path from registry root (e.g. "projects/alpha.md")
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, registry_dir)
                    file_list.append(rel_path)
                    
        return {"ok": True, "files": file_list}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_registry_read(state: AgentState, filename: str) -> Dict[str, Any]:
    """Read a specific Registry file."""
    try:
        # Secure Path Joining
        registry_dir = os.path.join(state.agent_fs_root, "data", "permanent")
        path = os.path.abspath(os.path.join(registry_dir, filename))
        
        # Security: Prevent traversing out of permanent dir
        if not path.startswith(registry_dir):
             return {"ok": False, "error": "Access denied: Path outside registry."}

        if not os.path.exists(path):
            return {"ok": False, "error": f"File '{filename}' does not exist."}
        
        with open(path, "r") as f:
            content = f.read()
        return {"ok": True, "content": content}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_registry_append(state: AgentState, filename: str, text: str) -> Dict[str, Any]:
    """Append text to a Registry file (creating it and parent dirs if needed)."""
    try:
        registry_dir = os.path.join(state.agent_fs_root, "data", "permanent")
        
        # Handle Nested Paths
        path = os.path.abspath(os.path.join(registry_dir, filename))
        if not path.startswith(registry_dir):
             return {"ok": False, "error": "Access denied: Path outside registry."}

        # Ensure parent dir exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Ensure extension
        if "." not in filename and not filename.endswith(".md"):
            path += ".md"
            
        entry = f"\n- {text}"
        
        with open(path, "a") as f:
            f.write(entry)
            
        if hasattr(state, "engine_ref") and state.engine_ref:
             if hasattr(state.engine_ref, "registry_cache"):
                 state.engine_ref.registry_cache = None

        return {"ok": True, "message": f"Appended to {filename}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def tool_registry_write(state: AgentState, filename: str, content: str) -> Dict[str, Any]:
    """Overwrite a Registry file completely (creating parent dirs if needed)."""
    try:
        registry_dir = os.path.join(state.agent_fs_root, "data", "permanent")
        path = os.path.abspath(os.path.join(registry_dir, filename))
        
        if not path.startswith(registry_dir):
             return {"ok": False, "error": "Access denied: Path outside registry."}
             
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "w") as f:
            f.write(content)
            
        if hasattr(state, "engine_ref") and state.engine_ref:
             if hasattr(state.engine_ref, "registry_cache"):
                 state.engine_ref.registry_cache = None
                 
        return {"ok": True, "message": f"Wrote {filename}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
