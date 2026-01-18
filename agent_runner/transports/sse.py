import asyncio
import json
import logging
from typing import Any, Dict, Optional, AsyncIterator

from agent_runner.state import AgentState
from agent_runner.transports.circuit_breaker import record_mcp_failure, reset_mcp_success

logger = logging.getLogger("agent_runner")


async def _parse_sse_events(stream) -> AsyncIterator[Dict[str, Any]]:
    """Yield parsed SSE events with optional 'event' and 'data' fields."""
    buffer = ""
    async for chunk in stream:
        buffer += chunk
        while "\n\n" in buffer:
            raw_event, buffer = buffer.split("\n\n", 1)
            event_type: Optional[str] = None
            data: Optional[str] = None
            for line in raw_event.split("\n"):
                if line.startswith("event: "):
                    event_type = line[len("event: ") :].strip()
                elif line.startswith("data: "):
                    data = line[len("data: ") :].strip()
            if data is not None:
                yield {"event": event_type or "message", "data": data}


async def call_sse_mcp(state: AgentState, server: str, url: str, rpc_body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """SSE transport aligned to the server's two-step protocol."""
    client = await state.get_http_client()
    sse_headers = headers.copy()
    sse_headers["Accept"] = "text/event-stream, application/json"
    sse_headers["Cache-Control"] = "no-cache"

    from agent_runner.constants import DEFAULT_RETRY_ATTEMPTS, SLEEP_BRIEF_BACKOFF_BASE

    max_retries = DEFAULT_RETRY_ATTEMPTS
    base_delay = SLEEP_BRIEF_BACKOFF_BASE

    for attempt in range(max_retries):
        try:
            # Step 1: Open SSE stream (GET)
            async with client.stream("GET", url, headers=sse_headers, timeout=state.http_timeout) as stream_response:
                if stream_response.status_code >= 400:
                    if stream_response.status_code >= 500 and attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))
                        continue
                    record_mcp_failure(state, server)
                    return {"ok": False, "status": stream_response.status_code, "error": f"HTTP {stream_response.status_code}"}

                endpoint_url: Optional[str] = None
                event_stream = _parse_sse_events(stream_response.aiter_text())

                # Step 2: Read initial endpoint event to get /mcp/messages URL
                async for event in event_stream:
                    if event["event"] == "endpoint":
                        try:
                            payload = json.loads(event["data"])
                            endpoint_url = payload.get("uri")
                        except Exception as e:
                            logger.warning(f"SSE endpoint parse failed: {e}")
                        break
                    # Ignore other events during handshake

                if not endpoint_url:
                    record_mcp_failure(state, server, error_context={"error": "missing endpoint event", "attempt": attempt + 1})
                    if attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))
                        continue
                    return {"ok": False, "error": "SSE handshake failed (no endpoint)"}

                # Step 3: POST the RPC body to the messages endpoint
                post_headers = headers.copy()
                post_headers["Content-Type"] = "application/json"
                post_resp = await client.post(endpoint_url, json=rpc_body, headers=post_headers, timeout=state.http_timeout)
                if post_resp.status_code >= 400:
                    record_mcp_failure(state, server)
                    return {"ok": False, "status": post_resp.status_code, "error": f"Message POST failed (HTTP {post_resp.status_code})"}

                # Step 4: Read SSE message events for matching id using same stream
                async for event in event_stream:
                    if event["event"] not in (None, "message", "event"):
                        continue
                    try:
                        data_obj = json.loads(event["data"])
                    except Exception:
                        continue

                    if data_obj.get("id") != rpc_body.get("id"):
                        continue

                    reset_mcp_success(state, server)
                    if "result" in data_obj:
                        return {"ok": True, "result": data_obj.get("result"), "id": data_obj.get("id")}
                    if "error" in data_obj:
                        return {"ok": False, "error": data_obj.get("error"), "id": data_obj.get("id")}

                # If stream closed without a matching message
                record_mcp_failure(state, server, error_context={"error": "no response message", "attempt": attempt + 1})
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
