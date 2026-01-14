import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from agent_runner.state import AgentState
from common.constants import MCP_SCHEME_HTTP, MCP_SCHEME_SSE, MCP_SCHEME_STDIO
from agent_runner.transports.http import call_http_mcp
from agent_runner.transports.sse import call_sse_mcp
from agent_runner.transports.stdio import get_or_create_stdio_process, initialize_stdio_process

from common.unified_tracking import track_event, EventSeverity, EventCategory

logger = logging.getLogger("agent_runner")

class PulseCheckFailed(Exception):
    """Raised when an MCP server fails its startup pulse check."""
    pass

async def perform_pulse_check(state: AgentState, server_name: str, config: Dict[str, Any]):
    """
    [DARWINIAN DISCOVERY] Pulse Check Protocol
    Briefly spin up the server to verify it doesn't crash immediately (e.g. missing API key).
    """
    logger.info(f"[Darwinian] Performing pulse check on '{server_name}'...")
    
    # Only check stdio servers for now as they are the most prone to env issues
    if config.get("type") != "stdio":
        return

    try:
        # 1. Attempt Spawn
        # We use a short timeout to catch immediate failures
        # Note: We reuse get_or_create to mimic exactly how the tool will be used later
        proc = await get_or_create_stdio_process(state, server_name, config["cmd"], config.get("env", {}))
        
        if not proc:
            raise PulseCheckFailed(f"Failed to spawn process for '{server_name}'")
            
        # 2. Strict Handshake (Initialize)
        # Instead of just waiting, we attempt the JSON-RPC initialization.
        # This guarantees the process is responsive and stdin/stdout are hooked up correctly.
        # If the process crashed (e.g. valid 'npx' wrapper but failed script), interact will fail.
        success = await initialize_stdio_process(state, server_name, proc)
        
        if not success:
             # Capture stderr usage if possible
             stderr_msg = "Handshake failed (Process died or timed out)"
             if proc.returncode is not None:
                try: 
                    # Try to grab stderr if it's dead
                    if proc.stderr:
                        err_bytes = await asyncio.wait_for(proc.stderr.read(4096), timeout=1.0)
                        stderr_msg += f": {err_bytes.decode('utf-8', errors='replace')}"
                except:
                    pass
             raise PulseCheckFailed(stderr_msg)
             
        # 3. Deep Check (List Tools)
        # Some servers (like brave-search) might initialize fine but crash when asked for tools if config is missing.
        # We perform a 'tools/list' call to ensure the server is truly functional.
        list_req = {
            "jsonrpc": "2.0", 
            "method": "tools/list", 
            "params": {}, 
            "id": int(time.time() * 1000) + 1
        }
        proc.stdin.write((json.dumps(list_req) + "\n").encode("utf-8"))
        await proc.stdin.drain()
        
        # Read response (iterative read to avoid buffering issues)
        # Give it 5 seconds as listing tools might load resources
        try:
             # Just read line by line until we find the response ID
             start_read = time.time()
             got_response = False
             while time.time() - start_read < 5.0:
                 line = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
                 if not line: # EOF
                     break
                 
                 try:
                     resp = json.loads(line.decode("utf-8", errors="replace"))
                     if resp.get("id") == list_req["id"]:
                         if "error" in resp:
                             raise PulseCheckFailed(f"Tool list returned error: {resp['error']}")
                         got_response = True
                         break
                 except json.JSONDecodeError:
                     continue
            
             if not got_response:
                 raise PulseCheckFailed("Failed to receive tool list response (Timeout or Crash)")
                 
        except asyncio.TimeoutError:
             raise PulseCheckFailed("Timeout waiting for tool list response")

        # 4. Success - Server survived the pulse check, handshake, and tool listing
        logger.info(f"[Darwinian] Server '{server_name}' PASSED pulse check (Handshake + Tool List OK).")
        
    except PulseCheckFailed:
        # Ensure we kill the process if it failed the check
        try:
             import signal
             if proc.returncode is None:
                 proc.send_signal(signal.SIGTERM)
        except: pass
        raise
    except Exception as e:
        try:
             import signal
             if proc.returncode is None:
                 proc.send_signal(signal.SIGTERM)
        except: pass
        raise PulseCheckFailed(f"Pulse check exception: {str(e)}")


async def tool_mcp_proxy(state: AgentState, server: str, tool: str, arguments: Dict[str, Any] = None, bypass_circuit_breaker: bool = False) -> Dict[str, Any]:
    """Proxy a tool call to a configured MCP server."""
    arguments = arguments or {}
    if not state.mcp_servers:
        return {"ok": False, "error": "No MCP servers configured"}
    cfg = state.mcp_servers.get(server)
    if not cfg:
        # This should not happen if tools are properly filtered, but log for user awareness
        logger.warning(f"MCP server '{server}' not found in configuration (tool should have been filtered)")
        return {"ok": False, "error": "Server not available"}

    # Check if server is disabled (before other checks)
    # This should not happen if tools are properly filtered, but log for user awareness
    if not cfg.get("enabled", True):
        reason = cfg.get("disabled_reason", "disabled in configuration")
        logger.warning(f"MCP server '{server}' is disabled: {reason} (tool should have been filtered)")
        # Notify user via tracking system
        track_event(
            event="mcp_server_disabled_attempt",
            message=f"Attempted to use disabled MCP server '{server}': {reason}",
            severity=EventSeverity.HIGH,
            category=EventCategory.MCP,
            component="mcp_proxy",
            metadata={"server": server, "tool": tool, "reason": reason}
        )
        return {"ok": False, "error": "Server disabled"}
    
    # Internet Check
    if cfg.get("requires_internet") and not state.internet_available:
        track_event(
            event="mcp_tool_blocked_offline",
            message=f"Blocked offline usage of {server}::{tool}",
            severity=EventSeverity.MEDIUM,
            category=EventCategory.MCP,
            component="mcp_proxy",
            metadata={"server": server, "tool": tool}
        )
        return {"ok": False, "error": "Internet unavailable"}

    # Fast binary health check (no timeout wait)
    if not bypass_circuit_breaker:
        health = state.mcp_server_health.get(server, {})
        
        # Check if health status is recent (within last 60s)
        last_check = health.get("last_check", 0)
        if time.time() - last_check > 60.0:
            # Health status is stale - make request anyway (with safety timeout)
            logger.debug(f"Health check for '{server}' is stale ({time.time() - last_check:.0f}s old)")
        
        if not health.get("healthy", False):
            error = health.get("error", "Server unavailable")
            logger.debug(f"MCP server '{server}' is unhealthy: {error}")
            return {"ok": False, "error": f"Server unavailable: {error}"}

    # Determine method
    if tool == "tools/list":
        method = "tools/list"
        params = {}
    else:
        method = "tools/call"
        params = {"name": tool, "arguments": arguments}

    rpc_body = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": int(time.time() * 1000),
    }

    scheme = cfg.get("scheme", cfg.get("type", MCP_SCHEME_HTTP))

    # Safety timeout wrapper (20s) - prevents runaway requests even if health check was wrong
    async def make_mcp_call():
        if scheme == MCP_SCHEME_HTTP:
            return await call_http_mcp(state, server, cfg["url"], rpc_body, {})
        elif scheme == MCP_SCHEME_SSE:
            return await call_sse_mcp(state, server, cfg["url"], rpc_body, {})
        elif scheme == MCP_SCHEME_STDIO:
            proc = await get_or_create_stdio_process(state, server, cfg["cmd"], cfg.get("env", {}))
            if not proc: 
                state.mcp_circuit_breaker.record_failure(server, weight=3, error="Failed to start stdio process")
                return {"ok": False, "error": "Failed to start stdio process"}
            
            if not await initialize_stdio_process(state, server, proc):
                state.mcp_circuit_breaker.record_failure(server, weight=2, error="Failed to initialize stdio process")
                return {"ok": False, "error": "Failed to initialize stdio process"}
            
            # Stdio communication logic
            if server not in state.stdio_process_locks:
                state.stdio_process_locks[server] = asyncio.Lock()

                # Add timeout to prevent indefinite deadlocks (10 seconds max wait)
            try:
                await asyncio.wait_for(state.stdio_process_locks[server].acquire(), timeout=10.0)
                try:
                    req_id = rpc_body["id"]
                    proc.stdin.write((json.dumps(rpc_body) + "\n").encode("utf-8"))
                    await proc.stdin.drain()
                    
                    res = {"ok": False, "error": "Did not receive a valid response from stdio process"}
                    
                    # Retrieve response line-by-line. 
                    # We loop to skip over potential debug/log lines from the server.
                    # BUT: If we hit a read timeout (silence), we must abort, not retry.
                    # [FIX] Use iterative read to avoid 64KB limit on readline()
                    buffer = b""
                    response_found = False
                    
                    start_time = time.time()
                    while time.time() - start_time < 30.0:
                        try:
                            chunk = await asyncio.wait_for(proc.stdout.read(65536), timeout=5.0)
                            if not chunk:
                                 if not buffer:
                                     break
                            
                            buffer += chunk
                            
                            while b'\n' in buffer:
                                line, buffer = buffer.split(b'\n', 1)
                                line_text = line.decode("utf-8", errors="replace").strip()
                                if not line_text:
                                    continue
                                    
                                try:
                                    data = json.loads(line_text)
                                    if data.get("id") == req_id:
                                        if "result" in data:
                                            res = {"ok": True, "result": data["result"]}
                                            response_found = True
                                        elif "error" in data:
                                            res = {"ok": False, "error": data["error"]["message"]}
                                            response_found = True
                                        break
                                except json.JSONDecodeError:
                                    continue 
                            
                            if response_found:
                                break
                                
                            if not chunk and not buffer:
                                break
                                
                        except asyncio.TimeoutError:
                            break # Timeout
                        except Exception as e:
                            logger.error(f"MCP Read Error: {e}")
                            break
                finally:
                    state.stdio_process_locks[server].release()
            except asyncio.TimeoutError:
                logger.error(f"Timeout acquiring lock for MCP stdio call '{server}' (10s). Possible deadlock.")
                return {"ok": False, "error": "Lock timeout - possible deadlock"}
            
            return res
        
        # Should not reach here - all schemes return
        return {"ok": False, "error": "Unknown transport scheme"}
    
    # Execute with safety timeout
    try:
        res = await asyncio.wait_for(make_mcp_call(), timeout=20.0)
    except asyncio.TimeoutError:
        # Safety timeout hit - mark unhealthy
        current_failures = state.mcp_server_health.get(server, {}).get("consecutive_failures", 0) + 1
        state.mcp_server_health[server] = {
            "healthy": False,
            "error": "Request timeout",
            "last_failure": time.time(),
            "last_check": time.time(),
            "consecutive_failures": current_failures
        }
        state.mcp_circuit_breaker.record_failure(server, weight=2, error="Request timeout")
        return {"ok": False, "error": "Request timeout"}
    except Exception as e:
        import traceback
        logger.error(f"Execution error in tool_mcp_proxy for {server}::{tool}: {traceback.format_exc()}")
        # Unexpected error - mark unhealthy immediately
        current_failures = state.mcp_server_health.get(server, {}).get("consecutive_failures", 0) + 1
        state.mcp_server_health[server] = {
            "healthy": False,
            "error": str(e),
            "last_failure": time.time(),
            "last_check": time.time(),
            "consecutive_failures": current_failures
        }
        state.mcp_circuit_breaker.record_failure(server, weight=2, error=e)
        return {"ok": False, "error": f"Transport error: {str(e)}"}
    
    return res

# Direct MCP server management tools (no MCP wrapper overhead)
async def tool_add_mcp_server(state: AgentState, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add or update an MCP server configuration directly.
    This bypasses the MCP server wrapper and calls state methods directly.
    """
    try:
        # Normalize config format (consistent with load_mcp_servers)
        if "command" in config:
            cmd = [config["command"]]
            if "args" in config:
                cmd.extend(config["args"])
            config["cmd"] = cmd
        
        # Add server (handles persistence to DB and disk)
        await state.add_mcp_server(name, config)
        
        # Nexus: Notify Discovery Start
        if hasattr(state, "system_event_queue"):
             await state.system_event_queue.put({
                 "event": {
                     "type": "system_status",
                     "content": f"🔍 Discovering tools for '{name}'...",
                     "severity": "info"
                 },
                 "request_id": None,
                 "timestamp": time.time()
             })

        # Trigger tool discovery
        from agent_runner.service_registry import ServiceRegistry
        try:
            engine = ServiceRegistry.get_engine()
            await engine.discover_mcp_tools()
            tool_count = len(engine.executor.mcp_tool_cache.get(name, []))

            # Nexus: Notify Discovery Success
            if hasattr(state, "system_event_queue"):
                 await state.system_event_queue.put({
                     "event": {
                         "type": "system_status",
                         "content": f"✅ MCP '{name}' ready: {tool_count} tools initialized.",
                         "severity": "info"
                     },
                     "request_id": None,
                     "timestamp": time.time()
                 })

            # [VECTOR-SEARCH] Index new tools immediately
            if hasattr(state, "vector_store") and state.vector_store:
                new_tools = engine.executor.mcp_tool_cache.get(name, [])
                if new_tools:
                    logger.info(f"[tool_add_mcp_server] Triggering vector indexing for {len(new_tools)} tools from '{name}'")
                    asyncio.create_task(state.vector_store.index_tools(new_tools))

        except RuntimeError:
            logger.warning("Could not access engine for tool discovery")
            tool_count = 0
        
        return {
            "ok": True,
            "message": f"Successfully added/updated MCP server '{name}'",
            "server": name,
            "tool_count": tool_count
        }
    except Exception as e:
        logger.error(f"Failed to add MCP server '{name}': {e}", exc_info=True)
        return {"ok": False, "error": str(e)}

async def tool_remove_mcp_server(state: AgentState, name: str) -> Dict[str, Any]:
    """
    Remove an MCP server configuration directly.
    Ensure process is terminated first.
    """
    try:
        # 1. Nexus: Notify User
        if hasattr(state, "system_event_queue"):
             await state.system_event_queue.put({
                 "event": {
                     "type": "system_status",
                     "content": f"🗑️ Removing MCP server '{name}'...",
                     "severity": "info"
                 },
                 "request_id": None,
                 "timestamp": time.time()
             })

        success = await state.remove_mcp_server(name)
        
        if success:
            # Clear tool cache
            from agent_runner.service_registry import ServiceRegistry
            try:
                engine = ServiceRegistry.get_engine()
                if name in engine.executor.mcp_tool_cache:
                    del engine.executor.mcp_tool_cache[name]
            except RuntimeError:
                logger.warning("Could not access engine to clear tool cache")
            
            return {
                "ok": True,
                "message": f"Successfully removed MCP server '{name}'",
                "server": name
            }
        else:
            return {"ok": False, "error": f"MCP server '{name}' not found"}
    except Exception as e:
        logger.error(f"Failed to remove MCP server '{name}': {e}", exc_info=True)
        return {"ok": False, "error": str(e)}

async def tool_install_mcp_package(state: AgentState, package: str, name: Optional[str] = None, args: Optional[List[str]] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Install an NPM-based MCP server package automatically.
    This bypasses the MCP server wrapper and calls state methods directly.
    """
    import asyncio
    
    # 1. Validate NPM package exists
    try:
        val_proc = await asyncio.create_subprocess_exec(
            "npm", "view", package, "name",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await val_proc.communicate()
        if val_proc.returncode != 0:
            return {"ok": False, "error": f"NPM package '{package}' not found"}
    except Exception as e:
        return {"ok": False, "error": f"NPM validation error: {str(e)}"}
    
    # 2. Derive server name if not provided
    if not name:
        if '@modelcontextprotocol/server-' in package:
            name = package.split('@modelcontextprotocol/server-')[1].split('@')[0]
        elif 'mcp-server-' in package:
            name = package.split('mcp-server-')[1].split('@')[0]
        else:
            name = package.split('/')[-1].replace('mcp-', '').replace('-mcp', '').split('@')[0]
    
    # 3. Construct config
    cmd_list = ["npx", "-y", package]
    if args:
        cmd_list.extend(args)
    
    config = {
        "cmd": cmd_list,
        "env": {},
        "enabled": True,
        "type": "stdio",
        "requires_internet": True
    }
    
    # Add API key if provided
    if api_key:
        if 'weather' in name.lower():
            config["cmd"].append(f"--api_key={api_key}")
        else:
            config["env"]["API_KEY"] = api_key
    
    # 4. Nexus: Notify User
    if hasattr(state, "system_event_queue"):
         await state.system_event_queue.put({
             "event": {
                 "type": "system_status",
                 "content": f"🚀 Installing MCP package '{package}' (this may take a moment)...",
                 "severity": "info"
             },
             "request_id": None,
             "timestamp": time.time()
         })

    # 5. Add server using direct tool
    return await tool_add_mcp_server(state, name, config)

async def tool_import_mcp_config(state: AgentState, raw_text: str) -> Dict[str, Any]:
    """
    Smartly parse and import MCP server configurations from raw text or JSON.
    This uses an LLM to interpret the input (e.g. "Install the weather server using npx...") 
    and updates the system configuration automatically.
    """
    try:
        from agent_runner.mcp_parser import parse_mcp_config_with_llm
        from agent_runner.config import load_mcp_servers
        from agent_runner.config_manager import ConfigManager
        
        # 1. Parse
        parsed_servers = await parse_mcp_config_with_llm(state, raw_text)
        if not parsed_servers:
            return {"ok": False, "error": "Could not identify any valid MCP server configurations in text."}
        
        # 2. Add each server (uses DB → Disk reverse sync)
        added = []
        for name, config in parsed_servers.items():
            await state.add_mcp_server(name, config)
            added.append(name)
        
        # 3. Reload System (Hot Reload)
        from agent_runner.service_registry import ServiceRegistry
        
        # Kill existing processes first
        await state.cleanup_all_stdio_processes()
        await load_mcp_servers(state)
        
        # Access engine via registry to trigger discovery
        try:
            engine = ServiceRegistry.get_engine()
            await engine.discover_mcp_tools()
            logger.info("[tool_import_mcp_config] Triggered MCP tool discovery on Engine.")
        except RuntimeError:
            logger.warning("[tool_import_mcp_config] Could not access AgentEngine from registry. Discovery skipped (requires manual reload).")
        
        return {
            "ok": True,
            "message": f"Successfully imported {len(parsed_servers)} servers: {added}. "
                       "Configuration saved and system reloaded.",
            "added": added
        }
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        return {"ok": False, "error": str(e)}
