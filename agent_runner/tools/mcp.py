import asyncio
import json
import logging
import time
from typing import Dict, Any
from agent_runner.state import AgentState
from common.constants import MCP_SCHEME_HTTP, MCP_SCHEME_SSE, MCP_SCHEME_STDIO
from agent_runner.transports.http import call_http_mcp
from agent_runner.transports.sse import call_sse_mcp
from agent_runner.transports.stdio import get_or_create_stdio_process, initialize_stdio_process

from common.unified_tracking import track_event, EventSeverity, EventCategory

logger = logging.getLogger("agent_runner")

async def tool_mcp_proxy(state: AgentState, server: str, tool: str, arguments: Dict[str, Any] = None, bypass_circuit_breaker: bool = False) -> Dict[str, Any]:
    """Proxy a tool call to a configured MCP server."""
    arguments = arguments or {}
    if not state.mcp_servers:
        return {"ok": False, "error": "No MCP servers configured"}
    cfg = state.mcp_servers.get(server)
    if not cfg:
        return {"ok": False, "error": f"Unknown MCP server '{server}'"}

    # Internet Check
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
        return {"ok": False, "error": f"Internet unavailable: Remote tool '{tool}' on server '{server}' is disabled."}

    # Circuit breaker check
    if not bypass_circuit_breaker:
        if not state.mcp_circuit_breaker.is_allowed(server):
            return {"ok": False, "error": f"MCP server '{server}' is currently disabled (circuit breaker open)"}

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

    try:
        if scheme == MCP_SCHEME_HTTP:
            res = await call_http_mcp(state, server, cfg["url"], rpc_body, {})
        elif scheme == MCP_SCHEME_SSE:
            res = await call_sse_mcp(state, server, cfg["url"], rpc_body, {})
        if scheme == MCP_SCHEME_STDIO:
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

            async with state.stdio_process_locks[server]:
                req_id = rpc_body["id"]
                proc.stdin.write((json.dumps(rpc_body) + "\n").encode("utf-8"))
                await proc.stdin.drain()
                
                res = {"ok": False, "error": "Did not receive a valid response from stdio process"}
                res = {"ok": False, "error": "Did not receive a valid response from stdio process"}
                
                # Retrieve response line-by-line. 
                # We loop to skip over potential debug/log lines from the server.
                # BUT: If we hit a read timeout (silence), we must abort, not retry.
                for _ in range(50): 
                    try:
                        line = await asyncio.wait_for(proc.stdout.readline(), timeout=30.0)
                        if not line:
                            break
                        line_text = line.decode("utf-8", errors="replace").strip()
                        if not line_text:
                            continue
                            
                        try:
                            data = json.loads(line_text)
                            if isinstance(data, dict) and data.get("id") == req_id:
                                if "error" in data:
                                    res = {"ok": False, "error": data["error"]}
                                else:
                                    res = {"ok": True, "result": data.get("result"), "id": data.get("id")}
                                break
                        except json.JSONDecodeError:
                            # Not JSON (likely log output), ignore and continue reading
                            continue
                            
                    except asyncio.TimeoutError:
                        logger.error(f"MCP Timeout: Server '{server}' silent for 30s.")
                        res = {"ok": False, "error": "MCP Request Timed Out (No response)"}
                        break
                    except Exception as e:
                        logger.error(f"MCP Read Error: {e}")
                        break

        # Handle result and update circuit breaker
        if res.get("ok"):
            state.mcp_circuit_breaker.record_success(server)
            return res
        else:
            # Check if it's a transient server error vs a logic error
            error_data = res.get("error", {})
            error_msg = str(error_data) if isinstance(error_data, dict) else str(error_data)
            
            # Logic errors (like tool not found or invalid params) shouldn't trip the breaker as easily
            is_logic_error = any(kw in error_msg.lower() for kw in ["not found", "invalid", "validation"])
            
            if not is_logic_error:
                state.mcp_circuit_breaker.record_failure(server, error=error_msg)
            
            return res

    except Exception as e:
        import traceback
        logger.error(f"Execution error in tool_mcp_proxy for {server}::{tool}: {traceback.format_exc()}")
        state.mcp_circuit_breaker.record_failure(server, weight=2, error=e)
        return {"ok": False, "error": f"Transport error: {str(e)}"}

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
        
        # 2. Save using ConfigManager (Source of Truth)
        manager = ConfigManager(state)
        success = await manager.save_mcp_config(parsed_servers)
        
        if not success:
            return {"ok": False, "error": "Failed to persist configuration to disk."}
            
        # 3. Reload System (Hot Reload)
        # Use ServiceRegistry to break circular dependency and access the Engine instance
        from agent_runner.registry import ServiceRegistry
        
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
            "message": f"Successfully imported {len(parsed_servers)} servers: {list(parsed_servers.keys())}. "
                       "Configuration saved and system reloaded.",
            "added": list(parsed_servers.keys())
        }
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        return {"ok": False, "error": str(e)}
