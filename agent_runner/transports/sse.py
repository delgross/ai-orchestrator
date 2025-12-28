import asyncio
import json
import time
import logging
import httpx
from typing import Dict, Any, Optional
from common.logging_utils import log_json_event as _log_json_event
from agent_runner.state import AgentState
from agent_runner.transports.circuit_breaker import record_mcp_failure, reset_mcp_success
from common.constants import MCP_SCHEME_SSE

logger = logging.getLogger("agent_runner")

async def call_sse_mcp(state: AgentState, server: str, url: str, rpc_body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """SSE transport logic."""
    client = await state.get_http_client()
    sse_headers = headers.copy()
    sse_headers["Accept"] = "text/event-stream, application/json"
    sse_headers["Cache-Control"] = "no-cache"
    
    max_retries = 3
    base_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            async with client.stream("POST", url, json=rpc_body, headers=sse_headers, timeout=state.http_timeout) as response:
                if response.status_code >= 400:
                    if response.status_code >= 500 and attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))
                        continue
                    record_mcp_failure(state, server)
                    return {"ok": False, "status": response.status_code, "error": f"HTTP {response.status_code}"}
                
                # Parse SSE Stream (Simplified for extraction)
                buffer = ""
                async for chunk in response.aiter_text():
                    buffer += chunk
                    if "\n\n" in buffer: # End of event
                        lines = buffer.split("\n")
                        for line in lines:
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    if data.get("id") == rpc_body["id"]:
                                        reset_mcp_success(state, server)
                                        return {"ok": True, "result": data.get("result"), "id": data.get("id")}
                                except: pass
                        buffer = ""
                
            record_mcp_failure(state, server, error_context={"error": "No valid SSE response", "attempt": attempt + 1})
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
                continue
            return {"ok": False, "error": "MCP SSE server did not return a valid response"}

        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
                continue
            record_mcp_failure(state, server)
            return {"ok": False, "error": f"Failed calling SSE MCP: {e}"}
            
    return {"ok": False, "error": "Max retries exceeded"}
