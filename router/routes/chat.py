import json
import logging
import time
from typing import Any, Dict

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio

from common.constants import (
    PREFIX_AGENT, PREFIX_OLLAMA, PREFIX_RAG,
    MODEL_AGENT_MCP, MODEL_ROUTER
)
from router.config import (
    state, AGENT_RUNNER_URL, AGENT_RUNNER_CHAT_PATH, 
    MAX_REQUEST_BODY_BYTES
)
from router.utils import join_url, sanitize_messages, parse_model_string, log_time
from router.providers import call_ollama_chat, call_ollama_chat_stream, provider_headers, retry_policy
from router.rag import call_rag

router = APIRouter(tags=["chat"])
logger = logging.getLogger("router.chat")

@router.post("/v1/chat/completions")
async def chat_completions(request: Request):
    # require_auth is handled at middleware level or called here
    from router.middleware import require_auth
    require_auth(request)
    
    # Check body size
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Request body too large")

    body = await request.json()
    model = body.get("model", "")
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.info(f"REQ [{request_id}] Chat Completion: Model='{model}'")
    
    if not model or model == "agent" or " " in model: 
        logger.warning(f"REQ [{request_id}] Invalid/Unknown model '{model}', defaulting to {MODEL_AGENT_MCP}")
        model = MODEL_AGENT_MCP
    
    # Resolve alias
    if model == MODEL_ROUTER:
        model = state.system_router_model
        
    prefix, model_id = parse_model_string(model)
    logger.debug(f"REQ [{request_id}] Parsed Target: Prefix='{prefix}', ID='{model_id}'")
    
    msgs = body.get("messages", [])
    body["messages"] = sanitize_messages(msgs)
    
    async with log_time(f"Chat Request [{request_id}]", level=logging.INFO):
        if state.semaphore:
            async with state.semaphore:
                return await _dispatch_chat(request, body, prefix, model_id)
        else:
            return await _dispatch_chat(request, body, prefix, model_id)

async def _dispatch_chat(request: Request, body: Dict[str, Any], prefix: str, model_id: str):
    """Decide whether to await response (Sync) or return 202 (Async) based on config."""
    is_async_mode = getattr(state, "router_mode", "sync") == "async"
    
    # Force Sync if streaming is requested (Async stream makes no sense unless we return a ticket, but for now we follow mode)
    # Actually, if streaming is requested, we MUST hold connection. Async mode skips streaming.
    if body.get("stream"):
        is_async_mode = False 
        
    if is_async_mode:
        # Fire and Forget
        # We need to run the handler in background.
        # Note: Request object might be closed? No, we extract data needed.
        # We launch a task that just hits the Agent Runner (ignoring response)
        asyncio.create_task(_background_chat_handler(body, prefix, model_id, getattr(request.state, "request_id", "bg")))
        return JSONResponse(
            status_code=202, 
            content={
                "id": f"chatcmpl-{int(time.time()*1000)}",
                "object": "chat.completion.async",
                "created": int(time.time()),
                "model": body.get("model"),
                "status": "accepted", 
                "message": "Request accepted for background processing."
            }
        )
    else:
        return await _handle_chat(request, body, prefix, model_id)

async def _background_chat_handler(body: Dict[str, Any], prefix: str, model_id: str, request_id: str):
    """Background task wrapper for Async Mode."""
    try:
        # We mock a request object? Or refactor _handle_chat to not need Request?
        # _handle_chat uses `request.state.request_id` and `state.client`.
        # Let's verify _handle_chat signature.
        # It takes `request`. Passing None might break it.
        # We should create a dummy request/state or refactor.
        # Refactoring _handle_chat is cleaner but risky for big file.
        # Let's just manually call the downstream logic since we know it's Agent Runner usually.
        
        # [Simulate Request]
        from dataclasses import dataclass
        @dataclass
        class MockState:
            request_id: str
        @dataclass
        class MockRequest:
            state: MockState
        
        mock_req = MockRequest(state=MockState(request_id=request_id))
        
        # We await it, but nobody listens to result. The result is "lost" to HTTP, but Side Effects (Logs/DB) happen.
        await _handle_chat(mock_req, body, prefix, model_id)
        logger.info(f"Background Task [{request_id}] completed.")
        
    except Exception as e:
        logger.error(f"Background Task [{request_id}] failed: {e}")



async def _handle_chat(request: Request, body: Dict[str, Any], prefix: str, model_id: str):
    request_id = getattr(request.state, "request_id", "unknown")

    if prefix == PREFIX_AGENT:
        # Route to agent runner
        url = join_url(AGENT_RUNNER_URL, AGENT_RUNNER_CHAT_PATH)
        
        # Check if streaming is requested
        if body.get("stream"):
            async def stream_wrapper():
                try:
                    # Proper streaming proxy using start.client.stream
                    headers = {"X-Request-ID": request_id}
                    async with state.client.stream("POST", url, json=body, headers=headers, timeout=120.0) as r:
                        if r.status_code >= 400:
                            # Handle error headers/early exit
                            err_msg = f"Agent returned {r.status_code}"
                            try:
                                content = await r.aread()
                                err_json = json.loads(content)
                                if "detail" in err_json: err_msg = err_json["detail"]
                            except: pass
                            
                            error_obj = {"error": {"message": err_msg, "type": "agent_error", "code": r.status_code}}
                            yield f"data: {json.dumps(error_obj)}\n\n"
                            yield "data: [DONE]\n\n"
                            return

                        # Stream the raw bytes from the agent (preserving SSE format)
                        async for chunk in r.aiter_bytes():
                            yield chunk
                            
                except Exception as e:
                    logger.error(f"Agent request failed: {e}")
                    error_obj = {"error": {"message": str(e), "type": "internal_server_error"}}
                    yield f"data: {json.dumps(error_obj)}\n\n"
                    pass

            return StreamingResponse(stream_wrapper(), media_type="text/event-stream")
            # Standard JSON proxy
            headers = {"X-Request-ID": request_id}
            try:
                r = await state.client.post(url, json=body, headers=headers, timeout=120.0)
                if r.status_code >= 500:
                   logger.warning(f"Agent Runner returned {r.status_code}. Returning 503 to client.")
                   return JSONResponse({"error": {"message": "Agent Runner Unavailable (Warming Up / Building)", "type": "service_unavailable", "code": 503}}, status_code=503)
                return JSONResponse(r.json(), status_code=r.status_code)
            except Exception as e:
                logger.error(f"Agent request failed (non-streaming): {e}")
                raise HTTPException(status_code=502, detail=f"Agent Runner Unavailable: {str(e)}")
    
    elif prefix == PREFIX_OLLAMA:
        if body.get("stream"):
            async def sse_generator():
                async for chunk in call_ollama_chat_stream(model_id, body["messages"], request_id):
                    yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(sse_generator(), media_type="text/event-stream")
        else:
            res = await call_ollama_chat(model_id, body["messages"], request_id)
            return JSONResponse(res)
        
    elif prefix == PREFIX_RAG:
        res = await call_rag(model_id, body)
        return JSONResponse(res)
    
    else:
        # Try finding in providers
        prov = state.providers.get(prefix)
        if prov:
            if not state.circuit_breakers.is_allowed(prefix):
                raise HTTPException(status_code=503, detail=f"Provider '{prefix}' is currently disabled via circuit breaker")

            state.provider_requests[prefix] = state.provider_requests.get(prefix, 0) + 1
            
            # BUDGET CHECK
            from common.budget import get_budget_tracker
            budget = get_budget_tracker()
            if not budget.check_budget():
                raise HTTPException(status_code=429, detail="Daily Budget Exceeded (Antigravity Cost Control)")

            url = join_url(prov.base_url, prov.chat_path)
            
            # Update body with the provider-specific model ID
            body["model"] = model_id
            
            # Check if streaming is requested
            if body.get("stream", False):
                # Passthrough with error tracking
                async def stream_gen():
                    try:
                        # Increased timeout to 120s for serverless cold boots (H100s)
                        async with state.client.stream("POST", url, headers=provider_headers(prov), json=body, timeout=120.0) as r:
                            if r.status_code >= 400:
                                state.circuit_breakers.record_failure(prefix)
                            else:
                                state.circuit_breakers.record_success(prefix)
                            
                            async for chunk in r.aiter_bytes():
                                yield chunk
                    except Exception as e:
                        state.circuit_breakers.record_failure(prefix)
                        logger.error(f"Provider {prefix} call failed: {e}")
                        raise
                return StreamingResponse(stream_gen(), media_type="text/event-stream")
            else:
                # Regular non-streaming request
                try:
                    @retry_policy
                    async def fetch_provider():
                        # Increased timeout to 120s for serverless cold boots (H100s)
                        r = await state.client.post(url, headers=provider_headers(prov), json=body, timeout=120.0)
                        if r.status_code == 429:
                           raise HTTPException(status_code=429, detail="Rate Limit")
                        if r.status_code >= 400:
                            state.circuit_breakers.record_failure(prefix)
                            raise HTTPException(status_code=r.status_code, detail=r.text)
                        return r

                    r = await fetch_provider()
                    
                    state.circuit_breakers.record_success(prefix)
                    data = r.json()
                    
                    # BUDGET RECORDING
                    try:
                        usage = data.get("usage", {})
                        in_tok = usage.get("prompt_tokens", 0)
                        out_tok = usage.get("completion_tokens", 0)
                        cost = budget.estimate_cost(body.get("model", ""), in_tok, out_tok)
                        if cost > 0:
                            budget.record_usage(prefix, cost)
                    except Exception:
                        pass
                    
                    return JSONResponse(data)
                except Exception as e:
                    state.circuit_breakers.record_failure(prefix)
                    logger.error(f"Provider {prefix} non-streaming call failed (swallowed 429 retries): {e}")
                    if isinstance(e, HTTPException):
                        raise
                    raise HTTPException(status_code=500, detail=str(e))
            
    raise HTTPException(status_code=404, detail=f"Provider or model not found: {prefix}:{model_id}")
