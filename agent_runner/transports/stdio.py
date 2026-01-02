import asyncio
import json
import time
import logging
import atexit
import weakref
from typing import Any, List, Dict
from common.logging_utils import log_json_event as _log_json_event
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner")

# [SAFETY] Global registry for atexit cleanup (in case of non-graceful shutdown)
_ACTIVE_SUBPROCESSES = set()

def _cleanup_on_exit():
    """Force kill all tracked subprocesses on interpreter exit."""
    if not _ACTIVE_SUBPROCESSES:
        return
    for proc in _ACTIVE_SUBPROCESSES:
        try:
            if proc.returncode is None:
                proc.kill()
        except Exception:
            pass

atexit.register(_cleanup_on_exit)


async def _log_stderr(server: str, stream: asyncio.StreamReader):
    """Background task to log stderr from an MCP process."""
    try:
        while True:
            line = await stream.readline()
            if not line:
                break
            decoded = line.decode('utf-8', errors='replace').strip()
            if decoded:
                logger.info(f"[MCP:{server}] {decoded}")
    except Exception as e:
        logger.debug(f"[MCP:{server}] Stderr logging failed: {e}")

async def get_or_create_stdio_process(state: AgentState, server: str, cmd: List[str], env: Dict[str, Any]) -> Any:
    """Get existing stdio process or create new one. Returns subprocess or None on error."""
    
    # Initialize lock for this server if needed
    if server not in state.stdio_process_locks:
        state.stdio_process_locks[server] = asyncio.Lock()
    
    async with state.stdio_process_locks[server]:
        # Check if process exists and is alive
        if server in state.stdio_processes:
            proc = state.stdio_processes[server]
            # Check if process is still running
            if proc.returncode is None:  # Process is still running
                return proc
            else:
                # Process died, cleanup immediately
                logger.debug(f"Stdio process for '{server}' died (returncode={proc.returncode}), cleaning up")
                await cleanup_stdio_process(state, server)
        
        # Create new process with merged environment
        proc = None
        try:
            # Merge provided env with system env (ensure PATH is preserved)
            import os
            full_env = os.environ.copy()
            if env:
                full_env.update({k: str(v) for k, v in env.items()})
            
            logger.info(f"DEBUG: Spawning {cmd} with env vars: {list(env.keys()) if env else 'None'}")
            print(f"DEBUG: SPAWNING CMD: {cmd}")

            async with state.mcp_subprocess_semaphore:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=full_env,
                )
            
            # Give the process a moment to start up
            await asyncio.sleep(0.1)
            
            # Check if process died during startup
            if proc.returncode is not None:
                stderr_data = b""
                if proc.stderr:
                    try:
                        stderr_data = await asyncio.wait_for(proc.stderr.read(1024), timeout=1.0)
                    except Exception:
                        pass
                print(f"DEBUG: PROCESS DIED IMMEDIATELY. ReturnCode: {proc.returncode}. Stderr: {stderr_data}")
                logger.error(
                    f"Stdio process for '{server}' died immediately (returncode={proc.returncode}). "
                    f"Stderr: {stderr_data.decode('utf-8', errors='replace')[:500]}"
                )
                await cleanup_stdio_process(state, server)
                return None
            
            state.stdio_processes[server] = proc
            state.stdio_process_initialized[server] = False
            state.stdio_process_health[server] = time.time()
            
            # [SAFETY] Track for atexit cleanup
            _ACTIVE_SUBPROCESSES.add(proc)
            
            # Start stderr logging
            if proc.stderr:
                asyncio.create_task(_log_stderr(server, proc.stderr))
                
            _log_json_event("mcp_stdio_process_created", server=server)
            return proc
        except Exception as e:
            print(f"DEBUG: STDIO EXCEPTION: {e}")
            _log_json_event("mcp_stdio_start_error", server=server, error=str(e))
            if proc is not None:
                try:
                    if proc.stdin: proc.stdin.close()
                    if proc.stdout: proc.stdout.close()
                    if proc.stderr: proc.stderr.close()
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
            return None

async def initialize_stdio_process(state: AgentState, server: str, proc: Any) -> bool:
    """Initialize stdio process with MCP handshake. Returns True if successful."""
    
    if server not in state.stdio_process_locks:
        state.stdio_process_locks[server] = asyncio.Lock()
    
    async with state.stdio_process_locks[server]:
        if state.stdio_process_initialized.get(server, False):
            return True
        
        if proc.returncode is not None:
            return False
        
        try:
            assert proc.stdin is not None and proc.stdout is not None
            
            init_body = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                    "clientInfo": {"name": "agent-runner", "version": "0.3.0"},
                },
                "id": int(time.time() * 1000),
            }
            init_id = init_body["id"]
            
            proc.stdin.write((json.dumps(init_body) + "\n").encode("utf-8"))
            await proc.stdin.drain()
            
            try:
                init_resp_line = await asyncio.wait_for(proc.stdout.readline(), timeout=10.0)
            except asyncio.TimeoutError:
                logger.error(f"Stdio process for '{server}' initialization timeout")
                return False
            
            if not init_resp_line:
                return False
            
            init_data = json.loads(init_resp_line.decode("utf-8", errors="replace"))
            
            if isinstance(init_data, dict) and init_data.get("id") == init_id:
                notif = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
                proc.stdin.write((json.dumps(notif) + "\n").encode("utf-8"))
                await proc.stdin.drain()
                
                state.stdio_process_initialized[server] = True
                _log_json_event("mcp_stdio_process_initialized", server=server)
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to initialize stdio process for '{server}': {e}")
            return False

async def cleanup_stdio_process(state: AgentState, server: str) -> None:
    """Clean up stdio process for a server."""
    if server not in state.stdio_processes:
        return
    
    proc = state.stdio_processes[server]
    try:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
    except Exception:
        try: proc.kill()
        except Exception: pass
    
    try:
        if proc.stdin: proc.stdin.close()
        if proc.stdout: proc.stdout.close()
        if proc.stderr: proc.stderr.close()
    except Exception: pass
    
    if server in state.stdio_processes: del state.stdio_processes[server]
    if server in state.stdio_process_initialized: del state.stdio_process_initialized[server]
    if server in state.stdio_process_health: del state.stdio_process_health[server]
    
    # [SAFETY] Remove from global tracking
    if proc in _ACTIVE_SUBPROCESSES:
        _ACTIVE_SUBPROCESSES.discard(proc)
    
    _log_json_event("mcp_stdio_process_cleaned", server=server)
