import asyncio
import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger("tools.node")

async def run_node(state: Any, code: str, dependency_check: bool = True) -> Dict[str, Any]:
    """
    Execute a Node.js script.
    
    Features:
    - Runs arbitrary JavaScript.
    - Optional: Minimal dependency management (if code has imports, user must provide package.json or we infer?).
    - Returns stdout/stderr.
    
    Args:
        state: AgentState
        code: JavaScript code to run
        dependency_check: If True, warns about missing node_modules if imports detected (Basic).
    """
    
    # 1. Create Isolation (Temp Directory)
    # We use a temp dir to avoid polluting the workspace unless requested.
    # TODO: In future, allow running in specific CWD.
    # For now, we run in a temp dir to be safe "Sandboxed execution".
    
    # Actually, for "Sovereign" dev, we often want to run in the PROJECT ROOT to access files.
    # Let's default to running in a temp file inside the FS_ROOT or CWD 
    # so we can access project files if we use relative paths.
    
    # Safe Strategy: Write script to a .tmp file in CWD, run it, then delete it.
    cwd = Path(os.getcwd())
    if hasattr(state, "agent_fs_root"):
        cwd = state.agent_fs_root 
        
    # Ensure CWD exists
    cwd.mkdir(parents=True, exist_ok=True)
    
    script_path = cwd / f"temp_script_{os.getpid()}.js"
    
    try:
        # 2. Write Code
        with open(script_path, "w") as f:
            f.write(code)
            
        # 3. Execution
        # We run with 'node' which we verified exists.
        # We assume dependencies (node_modules) are in CWD or parent.
        
        proc = await asyncio.create_subprocess_exec(
            "node",
            str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd)
        )
        
        stdout, stderr = await proc.communicate()
        
        output = stdout.decode().strip()
        error = stderr.decode().strip()
        
        result = {
            "ok": proc.returncode == 0,
            "stdout": output,
            "stderr": error,
            "code": proc.returncode
        }
        
        if proc.returncode != 0:
            logger.warning(f"Node script failed: {error}")
            
        return result

    except Exception as e:
        logger.error(f"Node Execution Error: {e}")
        return {"ok": False, "error": str(e)}
        
    finally:
        # Cleanup
        if script_path.exists():
            try:
                os.remove(script_path)
            except Exception:
                pass

async def run_npm(state: Any, command: str) -> Dict[str, Any]:
    """
    Run NPM commands (install, init, etc).
    """
    cwd = Path(os.getcwd())
    if hasattr(state, "agent_fs_root"):
        cwd = state.agent_fs_root
        
    try:
        cmd_parts = ["npm"] + command.split()
        
        proc = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd)
        )
        
        stdout, stderr = await proc.communicate()
        
        return {
            "ok": proc.returncode == 0,
            "stdout": stdout.decode().strip(),
            "stderr": stderr.decode().strip(),
            "code": proc.returncode
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
