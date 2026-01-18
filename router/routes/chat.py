import json
import logging
import time
from typing import Any, Dict, Union

from fastapi import APIRouter, Request, HTTPException
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
from common.constants import TIMEOUT_HTTP_LONG
from router.utils import join_url, sanitize_messages, parse_model_string
from router.providers import call_ollama_chat, call_ollama_chat_stream, provider_headers, retry_policy
from router.rag import call_rag
from common.logging_utils import log_time

router = APIRouter(tags=["chat"])
logger = logging.getLogger("router.chat")


def validate_chat_completion_request(body: Dict[str, Any]) -> Union[str, None]:
    """
    Validate chat completion request structure.
    Returns error message string if invalid, None if valid.
    """
    # Check messages field
    messages = body.get("messages")
    if not messages:
        return "messages field is required and cannot be empty"

    if not isinstance(messages, list):
        return "messages must be an array"

    if len(messages) == 0:
        return "messages array cannot be empty"

    # Validate each message
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            return f"message at index {i} must be an object"

        if "role" not in msg:
            return f"message at index {i} missing required 'role' field"

        if "content" not in msg:
            return f"message at index {i} missing required 'content' field"

        role = msg.get("role")
        if role not in ["system", "user", "assistant", "tool"]:
            return f"message at index {i} has invalid role '{role}'. Must be one of: system, user, assistant, tool"

        content = msg.get("content")
        if content is None:
            return f"message at index {i} content cannot be null"

    # Check model field (optional but should be reasonable if provided)
    model = body.get("model")
    if model is not None and not isinstance(model, str):
        return "model must be a string if provided"

    # Check stream field
    stream = body.get("stream")
    if stream is not None and not isinstance(stream, bool):
        return "stream must be a boolean if provided"

    # Check max_tokens
    max_tokens = body.get("max_tokens")
    if max_tokens is not None:
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            return "max_tokens must be a positive integer if provided"

    # Check temperature
    temperature = body.get("temperature")
    if temperature is not None:
        if not isinstance(temperature, (int, float)) or not (0.0 <= temperature <= 2.0):
            return "temperature must be a number between 0.0 and 2.0 if provided"

    return None  # Valid request

@router.post("/v1/chat/completions")
async def chat_completions(request: Request):
    print("DEBUG: Router chat_completions called!")
    try:
        # require_auth is handled at middleware level or called here
        from router.middleware import require_auth
        require_auth(request)

        # Check body size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
            raise HTTPException(status_code=413, detail="Request body too large")

        body = await request.json()

        # INPUT VALIDATION: Check chat completion request structure
        validation_error = validate_chat_completion_request(body)
        if validation_error:
            logger.warning(f"REQ [{request_id}] Invalid request: {validation_error}")
            return JSONResponse({
                "error": {
                    "message": validation_error,
                    "type": "invalid_request_error",
                    "code": 400
                }
            }, status_code=400)

        model = body.get("model", "")
        if isinstance(model, list):
            # Some clients might send an array; take first non-empty string
            model = next((str(m) for m in model if m), "")
        # Human-friendly alias support
        if model == "Questionable Insight":
            # Use agent:mcp for full agent processing
            model = "agent:mcp"


        # Strip extra quotes if present (client-side artifact)
        if model:
            model = model.strip('"\'')
        else:
            # Default model if none specified
            model = "agent:mcp"

        request_id = getattr(request.state, "request_id", "unknown")

        logger.info(f"REQ [{request_id}] Chat Completion: Model='{model}' Stream={body.get('stream', False)}")
    except Exception as e:
        logger.error(f"Early failure in chat_completions: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


    if not model or model == "agent" or " " in model: 
        logger.warning(f"REQ [{request_id}] Invalid/Unknown model '{model}', defaulting to {MODEL_AGENT_MCP}")
        model = MODEL_AGENT_MCP
    
    # Resolve alias
    if model == MODEL_ROUTER:
        model = state.system_router_model

    prefix, model_id = parse_model_string(model)
    logger.debug(f"REQ [{request_id}] Parsed Target: Prefix='{prefix}', ID='{model_id}'")

    # Parse quality tier from headers
    quality_tier = None
    quality_tier_header = request.headers.get("X-Quality-Tier", "").lower()
    if quality_tier_header:
        try:
            from agent_runner.quality_tiers import QualityTier
            quality_tier = QualityTier(quality_tier_header)
            logger.debug(f"REQ [{request_id}] Quality Tier: {quality_tier.value}")
        except Exception as e:
            logger.warning(f"REQ [{request_id}] Quality tier processing failed for '{quality_tier_header}': {e}")
            quality_tier = None

    msgs = body.get("messages", [])
    body["messages"] = sanitize_messages(msgs)
    
    try:
        async with log_time(f"Chat Request [{request_id}]", level=logging.INFO):
            if state.semaphore:
                async with state.semaphore:
                    return await _dispatch_chat(request, body, prefix, model_id, quality_tier)
            else:
                return await _dispatch_chat(request, body, prefix, model_id, quality_tier)
    except HTTPException:
        # Re-raise HTTP exceptions so FastAPI handles them correctly (e.g. 404, 401)
        raise
    except Exception as e:
        logger.error(f"Unhandled exception in chat_completions: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return JSONResponse({"error": {"message": str(e), "type": "internal_server_error"}}, status_code=500)

async def _dispatch_chat(request: Request, body: Dict[str, Any], prefix: str, model_id: str, quality_tier=None):
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
        asyncio.create_task(_background_chat_handler(body, prefix, model_id, getattr(request.state, "request_id", "bg"), quality_tier))
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
        return await _handle_chat(request, body, prefix, model_id, quality_tier)

async def _background_chat_handler(body: Dict[str, Any], prefix: str, model_id: str, request_id: str, quality_tier=None) -> None:
    """Background task wrapper for Async Mode."""
    try:
        # Call _handle_chat directly with request_id instead of mock request object
        await _handle_chat_internal(request_id, body, prefix, model_id, quality_tier)
        logger.info(f"Background Task [{request_id}] completed.")

    except Exception as e:
        logger.error(f"Background Task [{request_id}] failed: {e}")


async def _handle_chat(request: Request, body: Dict[str, Any], prefix: str, model_id: str, quality_tier=None):
    """Handle chat request with FastAPI Request object."""
    request_id = getattr(request.state, "request_id", "unknown")
    return await _handle_chat_internal(request_id, body, prefix, model_id, quality_tier)


async def _handle_chat_internal(request_id: str, body: Dict[str, Any], prefix: str, model_id: str, quality_tier=None):
    """Internal chat handler that doesn't require Request object."""

    if prefix == PREFIX_AGENT:
        # Route to agent runner
        url = join_url(AGENT_RUNNER_URL, AGENT_RUNNER_CHAT_PATH)

        # Check if streaming is requested
        stream_flag = body.get("stream")
        logger.info(f"REQ [{request_id}] Stream flag: {stream_flag} (type: {type(stream_flag)})")
        if stream_flag:
            async def stream_wrapper():
                try:
                    headers = {"X-Request-ID": request_id}
                    if quality_tier:
                        headers["X-Quality-Tier"] = quality_tier.value
                    logger.info(f"REQ [{request_id}] Forwarding SSE stream to Agent Runner...")
                    t_start = time.time()
                    first_byte = True

                    async with state.client.stream("POST", url, json=body, headers=headers, timeout=TIMEOUT_HTTP_LONG) as r:
                        if r.status_code >= 400:
                            # Handle non-200 responses in streaming
                            error_content = await r.aread()
                            try:
                                error_data = json.loads(error_content.decode('utf-8'))
                                error_obj = {"error": error_data.get("error", {"message": "Streaming request failed", "type": "internal_server_error"})}
                            except:
                                error_obj = {"error": {"message": f"HTTP {r.status_code}: Streaming failed", "type": "internal_server_error"}}
                            yield f"data: {json.dumps(error_obj)}\n\n"
                            return

                        # Forward SSE data as-is
                        async for chunk in r.aiter_bytes():
                            if first_byte:
                                duration = time.time() - t_start
                                logger.info(f"REQ [{request_id}] 🚀 TTFT (Agent -> Router): {duration:.4f}s")
                                first_byte = False

                            # Yield raw bytes directly
                            yield chunk

                except Exception as e:
                    logger.error(f"REQ [{request_id}] SSE streaming failed: {e}")
                    error_obj = {"error": {"message": f"Streaming failed: {str(e)}", "type": "internal_server_error"}}
                    yield f"data: {json.dumps(error_obj)}\n\n"

            return StreamingResponse(stream_wrapper(), media_type="text/event-stream")

        # Standard JSON proxy
        headers = {"X-Request-ID": request_id}
        if quality_tier:
            headers["X-Quality-Tier"] = quality_tier.value
        try:
            r = await state.client.post(url, json=body, headers=headers, timeout=TIMEOUT_HTTP_LONG)

            # Handle different HTTP status codes appropriately
            if r.status_code >= 500:
                # 5xx = Server errors (service unavailable)
                logger.warning(f"REQ [{request_id}] Agent Runner returned {r.status_code}. Returning 503 to client.")
                return JSONResponse({
                    "error": {
                        "message": "Agent Runner Unavailable (Warming Up / Building)",
                        "type": "service_unavailable",
                        "code": 503
                    }
                }, status_code=503)

            elif r.status_code >= 400:
                # 4xx = Client errors (forward the actual error from agent runner)
                logger.warning(f"REQ [{request_id}] Agent Runner returned {r.status_code} (client error)")
                try:
                    error_data = r.json()
                    return JSONResponse(error_data, status_code=r.status_code)
                except:
                    # If we can't parse the error response, return a generic one
                    return JSONResponse({
                        "error": {
                            "message": f"Request validation failed (HTTP {r.status_code})",
                            "type": "invalid_request_error",
                            "code": r.status_code
                        }
                    }, status_code=r.status_code)

            else:
                # 2xx = Success
                response_data = r.json()
                logger.info(f"ROUTER: Forwarding response with keys: {list(response_data.keys()) if isinstance(response_data, dict) else type(response_data)}")
                if isinstance(response_data, dict) and "metadata" in response_data:
                    logger.warning(f"ROUTER: Response contains non-standard 'metadata' field - this may cause client parsing issues")
                return JSONResponse(response_data, status_code=r.status_code)
        except Exception as e:
            logger.error(f"Agent request failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return JSONResponse({"error": {"message": str(e), "type": "internal_server_error"}}, status_code=500)

    elif prefix == PREFIX_OLLAMA:
        # [PATCH] Extract extra params for Ollama (keep_alive, options)
        extra_kwargs = {}
        if "keep_alive" in body:
            extra_kwargs["keep_alive"] = body["keep_alive"]
        if "options" in body:
            extra_kwargs["options"] = body["options"]

        if body.get("stream"):
            async def sse_generator():
                async for chunk in call_ollama_chat_stream(model_id, body["messages"], request_id, **extra_kwargs):
                    yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(sse_generator(), media_type="text/event-stream")
        else:
            res = await call_ollama_chat(model_id, body["messages"], request_id, **extra_kwargs)
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
                        async with state.client.stream("POST", url, headers=provider_headers(prov), json=body, timeout=TIMEOUT_HTTP_LONG) as r:
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
                        r = await state.client.post(url, headers=provider_headers(prov), json=body, timeout=TIMEOUT_HTTP_LONG)
                        if r.status_code == 429:
                            # Pass Retry-After header through exception for wait_retry_after_header
                            retry_after = r.headers.get("Retry-After")
                            detail = {"error": "Rate Limit", "retry_after": retry_after} if retry_after else "Rate Limit"
                            raise HTTPException(status_code=429, detail=detail)
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
                    except Exception as e:
                        logger.warning(f"Budget recording failed: {e}")
                    
                    return JSONResponse(data)
                except Exception as e:
                    state.circuit_breakers.record_failure(prefix)
                    logger.error(f"Provider {prefix} non-streaming call failed (swallowed 429 retries): {e}")
                    if isinstance(e, HTTPException):
                        raise
                    raise HTTPException(status_code=500, detail=str(e))

    # [NEW] Universal hallucination detection for all chat responses
    logger.warning(f"HALLUCINATION_CHECK: Processing {prefix} response")
    try:
        # Apply to all response types that have content
        response_to_check = None
        messages_for_context = body.get("messages", [])

        if prefix == PREFIX_AGENT:
            # Agent responses come as JSONResponse objects
            if 'result' in locals() and isinstance(result, dict):
                response_to_check = result
                logger.warning("HALLUCINATION_CHECK: Found agent result to check")
        elif prefix == PREFIX_OLLAMA:
            # Ollama responses come as data dict
            if 'data' in locals() and isinstance(data, dict):
                response_to_check = data
                logger.warning("HALLUCINATION_CHECK: Found ollama data to check")

        if response_to_check and isinstance(response_to_check, dict):
            logger.warning("HALLUCINATION_CHECK: Checking response for hallucinations")
            if (response_to_check.get("object") == "chat.completion" and
                response_to_check.get("choices") and
                len(response_to_check["choices"]) > 0):

                choice = response_to_check["choices"][0]
                message = choice.get("message", {})
                content = message.get("content", "")

                if content and len(content.strip()) > 10:  # Only check substantial responses
                    # Import hallucination detector
                    from agent_runner.hallucination_detector import HallucinationDetector, DetectorConfig

                    # Get shared state
                    try:
                        from router.config import state as router_state
                        detector_config = DetectorConfig(enabled=True)
                        detector = HallucinationDetector(router_state, detector_config)

                        # Prepare context for detection
                        user_messages = [msg for msg in messages_for_context if msg.get("role") == "user"]
                        user_query = user_messages[-1]["content"] if user_messages else ""

                        context = {
                            "response": content,
                            "user_query": user_query,
                            "conversation_history": messages_for_context[:-1] if len(messages_for_context) > 1 else [],
                            "model_info": {"model": requested_model or "unknown"}
                        }

                        # Run hallucination detection
                        logger.warning("HALLUCINATION_CHECK: Starting detection")
                        detection_result = await detector.detect_hallucinations(**context)
                        logger.warning(f"HALLUCINATION_CHECK: Detection completed - hallucination: {detection_result.is_hallucination}")

                        # Log detection results
                        if detection_result.is_hallucination:
                            logger.warning(f"HALLUCINATION DETECTED in {prefix} response: severity={detection_result.severity.value}, confidence={detection_result.confidence:.2f}")

                            # For critical hallucinations, replace with safe response
                            if detection_result.severity.value == "critical":
                                logger.warning("HALLUCINATION_CHECK: Replacing with safe response")
                                choice["message"]["content"] = "I apologize, but I cannot provide accurate information about that topic. Please consult the official documentation or try rephrasing your question."
                                choice["message"]["hallucination_detected"] = True
                            elif detection_result.severity.value == "high":
                                logger.warning("HALLUCINATION_CHECK: Adding warning to response")
                                # Add warning but keep original response
                                choice["message"]["content"] += "\n\n⚠️ *Note: This response may contain inaccuracies. Please verify the information.*"
                                choice["message"]["hallucination_warning"] = True

                        # Skip adding metadata to maintain OpenAI compatibility
                        logger.warning(f"HALLUCINATION_CHECK: Detection completed (metadata skipped for compatibility)")

                        # Cleanup
                        await detector.cleanup()
                        logger.warning("HALLUCINATION_CHECK: Cleanup completed")

                    except Exception as detect_e:
                        logger.error(f"HALLUCINATION_CHECK: Detection failed: {detect_e}")
                        import traceback
                        logger.error(f"HALLUCINATION_CHECK: Traceback: {traceback.format_exc()}")
                        # Don't fail the request if detection fails

    except Exception as post_e:
        logger.error(f"Post-processing failed: {post_e}")
        # Don't fail the request if post-processing fails

    raise HTTPException(status_code=404, detail=f"Provider or model not found: {prefix}:{model_id}")


async def check_streaming_health() -> Dict[str, Any]:
    """Check streaming functionality health by testing a simple streaming request."""
    try:
        # Test streaming by making a simple request to agent runner
        url = join_url(AGENT_RUNNER_URL, AGENT_RUNNER_CHAT_PATH)
        test_body = {
            "model": "qwen2.5:7b-instruct",
            "messages": [{"role": "user", "content": "test"}],
            "stream": True,
            "max_tokens": 5
        }

        # Try to make a streaming request with a short timeout
        async with state.client.stream("POST", url, json=test_body, timeout=5.0) as r:
            if r.status_code >= 400:
                return {"ok": False, "error": f"HTTP {r.status_code}"}

            # Try to read first chunk to verify streaming works
            try:
                chunk = await r.aiter_bytes().__anext__()
                return {"ok": True, "chunk_received": len(chunk) > 0}
            except StopAsyncIteration:
                return {"ok": False, "error": "No chunks received"}
            except Exception as e:
                return {"ok": False, "error": f"Chunk read failed: {str(e)}"}

    except Exception as e:
        return {"ok": False, "error": str(e)}
