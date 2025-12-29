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

async def tool_mcp_proxy(state: AgentState, server: str, tool: str, arguments: Dict[str, Any], bypass_circuit_breaker: bool = False) -> Dict[str, Any]:
    """Proxy a tool call to a configured MCP server."""
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
                for _ in range(20): # increased from 10
                    try:
                        line = await asyncio.wait_for(proc.stdout.readline(), timeout=30.0)
                        if not line:
                            break
                        line_text = line.decode("utf-8", errors="replace").strip()
                        if not line_text:
                            continue
                            
                        data = json.loads(line_text)
                        if isinstance(data, dict) and data.get("id") == req_id:
                            if "error" in data:
                                res = {"ok": False, "error": data["error"]}
                            else:
                                res = {"ok": True, "result": data.get("result"), "id": data.get("id")}
                            break
                    except (asyncio.TimeoutError, json.JSONDecodeError):
                        continue
        else:
            return {"ok": False, "error": f"Unsupported transport scheme: {scheme}"}

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
        logger.error(f"Execution error in tool_mcp_proxy for {server}::{tool}: {e}")
        state.mcp_circuit_breaker.record_failure(server, weight=2, error=e)
        return {"ok": False, "error": f"Transport error: {str(e)}"}
