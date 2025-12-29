import asyncio
import httpx
import logging
from typing import Dict, Any
from common.logging_utils import log_json_event as _log_json_event
from agent_runner.state import AgentState
from agent_runner.transports.circuit_breaker import record_mcp_failure, reset_mcp_success

logger = logging.getLogger("agent_runner")

async def call_http_mcp(state: AgentState, server: str, url: str, rpc_body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """HTTP transport with retry logic."""
    client = await state.get_http_client()
    max_retries = 3
    base_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            resp = await client.post(url, json=rpc_body, headers=headers, timeout=state.http_timeout)
            
            if resp.status_code >= 400:
                is_retryable = resp.status_code >= 500
                _log_json_event("mcp_http_error", server=server, status_code=resp.status_code, attempt=attempt+1)
                
                if is_retryable and attempt < max_retries - 1:
                    await asyncio.sleep(base_delay * (2 ** attempt))
                    continue
                else:
                    record_mcp_failure(state, server)
                    try: detail = resp.json()
                    except: detail = resp.text
                    return {"ok": False, "status": resp.status_code, "error": detail}
            
            data = resp.json()
            reset_mcp_success(state, server)
            return {"ok": True, "result": data.get("result"), "id": data.get("id")}
            
        except (httpx.ConnectError, httpx.NetworkError, httpx.TimeoutException) as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
                continue
            record_mcp_failure(state, server, error_context={"error": str(e), "attempt": attempt + 1})
            return {"ok": False, "error": f"Failed to reach MCP server: {e}"}
        except Exception as e:
            record_mcp_failure(state, server)
            return {"ok": False, "error": f"Error calling MCP server: {e}"}
    
    return {"ok": False, "error": "Max retries exceeded"}
