import asyncio
import json
import time
import logging
import atexit
import weakref
from pathlib import Path
from typing import Any, List, Dict
from common.logging_utils import log_json_event as _log_json_event
from agent_runner.state import AgentState
from agent_runner.constants import (
    LOCK_ACQUISITION_TIMEOUT_SECONDS,
    ERROR_STDERR_READ_FAILED,
    ERROR_PROCESS_CREATION_FAILED,
    ERROR_PROCESS_STREAM_CLOSE_FAILED,
    PROCESS_INITIALIZATION_TIMEOUT_SECONDS,
    NON_CORE_PROCESS_TIMEOUT_SECONDS,
    PROCESS_WAIT_TIMEOUT_SECONDS,
    STDERR_READ_TIMEOUT_SECONDS
)

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
        except Exception as e:

            logger.debug(ERROR_STDERR_READ_FAILED.format(error=e))

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

# Servers that should maintain persistent connections (not killed after each call)
PERSISTENT_SERVERS = {"thinking", "sequential-thinking", "project-memory"}

async def get_or_create_stdio_process(state: AgentState, server: str, cmd: List[str], env: Dict[str, Any]) -> Any:
    """Get existing stdio process or create new one. Returns subprocess or None on error."""
    
    # Initialize lock for this server if needed
    if server not in state.stdio_process_locks:
        state.stdio_process_locks[server] = asyncio.Lock()
    
    # Track if we actually acquired the lock (for proper cleanup)
    lock_acquired = False
    
    # Add timeout to prevent indefinite deadlocks (10 seconds max wait)
    # Add timeout to prevent indefinite deadlocks (10 seconds max wait)
    # Add timeout to prevent indefinite deadlocks (10 seconds max wait)
    try:
        await asyncio.wait_for(state.stdio_process_locks[server].acquire(), timeout=LOCK_ACQUISITION_TIMEOUT_SECONDS)
        lock_acquired = True
        
        # Check if process exists and is alive
        if server in state.stdio_processes:
            proc = state.stdio_processes[server]
            # Check if process is still running
            if proc.returncode is None:  # Process is still running
                # For persistent servers, always reuse if alive
                if server in PERSISTENT_SERVERS:
                    logger.debug(f"Reusing persistent stdio process for '{server}'")
                    return proc
                # For non-persistent servers, return existing process (legacy behavior)
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
            
            # [FIX] Explicitly set npm cache environment variables for npx/uvx processes
            # This ensures npm cache is in the program environment even if not in os.environ
            if cmd and len(cmd) > 0:
                first_cmd = cmd[0] if isinstance(cmd, list) else str(cmd)
                if first_cmd in ('npx', 'uvx') or 'npx' in str(first_cmd) or 'uvx' in str(first_cmd):
                    # Load npm cache config from agent_runner.env if not already set
                    if 'npm_config_cache' not in full_env:
                        env_file = Path(__file__).parent.parent.parent / "agent_runner" / "agent_runner.env"
                        if env_file.exists():
                            try:
                                with open(env_file, 'r') as f:
                                    for line in f:
                                        line = line.strip()
                                        if line and not line.startswith('#') and '=' in line:
                                            key, value = line.split('=', 1)
                                            key = key.strip()
                                            value = value.strip().strip("'").strip('"')
                                            if key.startswith('npm_config_'):
                                                full_env[key] = value
                                                logger.debug(f"Loaded {key} from agent_runner.env: {value}")
                            except Exception as e:
                                logger.debug(f"Could not read agent_runner.env for npm config: {e}")
                        else:
                            # Fallback: use project-relative cache directory
                            project_root = Path(__file__).parent.parent.parent
                            cache_dir = project_root / ".npm_cache"
                            if cache_dir.exists():
                                full_env['npm_config_cache'] = str(cache_dir)
                                logger.debug(f"Set npm_config_cache to project cache: {cache_dir}")
            
            logger.debug(f"Spawning MCP server: cmd={cmd}, env_vars={list(env.keys()) if env else 'None'}")

            async with state.mcp_subprocess_semaphore:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=full_env,
                )
            
            # Give the process a moment to start up
            from agent_runner.constants import SLEEP_BRIEF_BACKOFF_BASE
            await asyncio.sleep(SLEEP_BRIEF_BACKOFF_BASE)
            
            # Check if process died during startup
            if proc.returncode is not None:
                stderr_data = b""
                if proc.stderr:
                    try:
                        stderr_data = await asyncio.wait_for(proc.stderr.read(1024), timeout=STDERR_READ_TIMEOUT_SECONDS)
                    except Exception as e:

                        logger.debug(ERROR_STDERR_READ_FAILED.format(error=e))
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
                from agent_runner.task_utils import create_safe_task
                create_safe_task(
                    _log_stderr(server, proc.stderr),
                    task_name=f"mcp_stderr_log_{server}",
                    log_errors=False  # Stderr logging failures are not critical
                )
                
            _log_json_event("mcp_stdio_process_created", server=server)
            
            # For persistent servers, log that we're keeping it alive
            if server in PERSISTENT_SERVERS:
                logger.info(f"Created persistent stdio process for '{server}' (will be reused)")
            
            return proc
        except Exception as e:
                logger.error(ERROR_PROCESS_CREATION_FAILED.format(error=e))
                _log_json_event("mcp_stdio_start_error", server=server, error=str(e))
                if proc is not None:
                    try:
                        if proc.stdin: proc.stdin.close()
                        if proc.stdout: proc.stdout.close()
                        if proc.stderr: proc.stderr.close()
                        proc.kill()
                        await proc.wait()
                    except Exception as e:

                        logger.debug(ERROR_STDERR_READ_FAILED.format(error=e))
                return None
                return None
    except asyncio.TimeoutError:
        logger.error(f"Timeout acquiring lock for stdio process '{server}' (10s). Possible deadlock.")
        return None
    finally:
        # Only release if we actually acquired the lock
        if lock_acquired:
            state.stdio_process_locks[server].release()

async def initialize_stdio_process(state: AgentState, server: str, proc: Any) -> bool:
    """Initialize stdio process with MCP handshake. Returns True if successful."""
    
    # If already initialized, skip re-init to avoid lock contention
    if state.stdio_process_initialized.get(server, False):
        return True
    
    if server not in state.stdio_process_locks:
        state.stdio_process_locks[server] = asyncio.Lock()
    
    # Track if we actually acquired the lock (for proper cleanup)
    lock_acquired = False
    
    # Add timeout to prevent indefinite deadlocks (10 seconds max wait)
    # Add timeout to prevent indefinite deadlocks (10 seconds max wait)
    # Add timeout to prevent indefinite deadlocks (10 seconds max wait)
    try:
        await asyncio.wait_for(state.stdio_process_locks[server].acquire(), timeout=LOCK_ACQUISITION_TIMEOUT_SECONDS)
        lock_acquired = True
        try:
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
                
                # Check if process is still alive before waiting (fast failure for dead processes)
                if proc.returncode is not None:  # Note: asyncio.subprocess.Process uses returncode, not poll()
                    logger.error(f"Stdio process for '{server}' died before initialization (returncode={proc.returncode})")
                    return False
                
                # Use longer timeout for initialization: 20s for core services, 15s for non-core
                from agent_runner.constants import CORE_MCP_SERVERS
                init_timeout = PROCESS_INITIALIZATION_TIMEOUT_SECONDS if server in CORE_MCP_SERVERS else NON_CORE_PROCESS_TIMEOUT_SECONDS
                
                try:
                    init_resp_line = await asyncio.wait_for(proc.stdout.readline(), timeout=init_timeout)
                except asyncio.TimeoutError:
                    # Check if process died during wait
                    if proc.returncode is not None:  # Note: asyncio.subprocess.Process uses returncode, not poll()
                        logger.error(f"Stdio process for '{server}' died during initialization (returncode={proc.returncode})")
                    else:
                        logger.error(f"Stdio process for '{server}' initialization timeout ({init_timeout}s) - process still running")
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
        finally:
            # Only release if we actually acquired the lock
            if lock_acquired:
                state.stdio_process_locks[server].release()
    except asyncio.TimeoutError:
        logger.error(f"Timeout acquiring lock for stdio initialization '{server}' (10s). Possible deadlock.")
        return False

async def cleanup_stdio_process(state: AgentState, server: str) -> None:
    """Clean up stdio process for a server."""
    if server not in state.stdio_processes:
        return
    
    proc = state.stdio_processes[server]
    try:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=PROCESS_WAIT_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
    except Exception as e:
        logger.debug(f"Error during process cleanup: {e}")
        try: proc.kill()
        except Exception as kill_err:
            logger.debug(f"Error killing process: {kill_err}")

    try:
        if proc.stdin: proc.stdin.close()
        if proc.stdout: proc.stdout.close()
        if proc.stderr: proc.stderr.close()
    except Exception as cleanup_err:
        logger.debug(ERROR_PROCESS_STREAM_CLOSE_FAILED.format(error=cleanup_err))
    
    if server in state.stdio_processes: del state.stdio_processes[server]
    if server in state.stdio_process_initialized: del state.stdio_process_initialized[server]
    if server in state.stdio_process_health: del state.stdio_process_health[server]
    
    # [SAFETY] Remove from global tracking
    if proc in _ACTIVE_SUBPROCESSES:
        _ACTIVE_SUBPROCESSES.discard(proc)
    
    _log_json_event("mcp_stdio_process_cleaned", server=server)
