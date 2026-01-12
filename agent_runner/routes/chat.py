import logging
import json
import time
import uuid
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from common.constants import OBJ_CHAT_COMPLETION, OBJ_MODEL
from common.logging_utils import log_time
from agent_runner.agent_runner import get_shared_state, get_shared_engine
from agent_runner.quality_eval import evaluate_completion
from agent_runner.models import ChatCompletionRequest, ChatCompletionResponse, ErrorResponse

router = APIRouter()
logger = logging.getLogger("agent_runner.chat")

@router.post("/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    logger.info(f"Chat completion request received: {list(body.keys())}")
    state = get_shared_state()
    engine = get_shared_engine()

    messages = body.get("messages", [])
    logger.info(f"Messages: {len(messages)} items")

    # Extract Request ID for distributed tracing
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())[:8]

    # Check for Bypass Header (Internal/System Requests)
    skip_refinement = request.headers.get("X-Skip-Refinement", "false").lower() == "true"

    # Check for Quality Tier Header
    quality_tier = None
    quality_tier_header = request.headers.get("X-Quality-Tier", "").lower()
    if quality_tier_header:
        try:
            from agent_runner.quality_tiers import QualityTier
            quality_tier = QualityTier(quality_tier_header)
        except ValueError:
            logger.warning(f"Invalid quality tier header: {quality_tier_header}")
            quality_tier = None

    # MINIMAL VALIDATION: Rate limiting only (very fast)
    rate_check = engine._check_rate_limits(request_id)
    if not rate_check["allowed"]:
        logger.warning(f"❌ Rate limit exceeded for request {request_id}")
        return JSONResponse({
            "error": {
                "message": "Rate limit exceeded. Please try again later.",
                "type": "rate_limit_exceeded",
                "code": 429
            }
        }, status_code=429)

    # Use the engine to process the request
    state.active_requests += 1
    state.last_interaction_time = time.time()
    
    # Timer for stats endpoint (distinct from log_time)
    t0_stats = time.time()
    
    try:
        requested_model = body.get(OBJ_MODEL)
        stream_mode = body.get("stream", False)
        
        logger.info(f"REQ [{request_id}] Agent Execution: Model='{requested_model}' Stream={stream_mode} SkipRefinement={skip_refinement}")

        # Prevent infinite recursion / invalid model names
        if requested_model == "agent:mcp" or not requested_model or ":" not in requested_model:
            requested_model = None
            
        if stream_mode:
            async def sse_wrapper():
                try:
                    async with log_time(f"Agent Stream [{request_id}]", level=logging.INFO, logger_override=logger):
                        # Propagate skip_refinement to stream
                        
                        # [PHASE 60] I/O Nexus Integration
                        # Extract the raw user input (last message) for trigger check
                        last_msg = messages[-1].get("content") if messages else ""
                        
                        # Check for system events to inject (from startup, health checks, etc.)
                        if hasattr(state, 'system_event_queue') and state.system_event_queue:
                            try:
                                # Non-blocking check for queued system events
                                while not state.system_event_queue.empty():
                                    sys_event_data = state.system_event_queue.get_nowait()
                                    # Only inject if request_id matches or is None (broadcast)
                                    if sys_event_data.get("request_id") is None or sys_event_data.get("request_id") == request_id:
                                        sys_event = sys_event_data.get("event", {})
                                        # Yield system event as a special chunk
                                        chunk = {
                                            "id": f"chatcmpl-{request_id}",
                                            "object": "chat.completion.chunk",
                                            "created": int(time.time()),
                                            "model": requested_model or "agent",
                                            "choices": [
                                                {
                                                    "index": 0,
                                                    "delta": sys_event,
                                                    "finish_reason": None
                                                }
                                            ]
                                        }
                                        yield f"data: {json.dumps(chunk)}\n\n"
                            except asyncio.QueueEmpty:
                                pass
                        
                        # Pass through the Nexus Regulator
                        # Nexus handles Trigger Checks -> Execution -> Engine Handoff
                        async for event in engine.nexus.dispatch(
                            user_message=last_msg,
                            request_id=request_id,
                            context=messages[:-1] # Nexus rebuilds context
                        ):
                            evt_type = event.get("type")

                            # Handle different event types from agent_stream
                            if evt_type == "done":
                                chunk = {
                                    "id": f"chatcmpl-{request_id}",
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": requested_model or "agent",
                                    "choices": [
                                        {
                                            "index": 0,
                                            "delta": {},
                                            "finish_reason": event.get("stop_reason", "stop")
                                        }
                                    ]
                                }
                                if "usage" in event:
                                    chunk["usage"] = event["usage"]
                                yield f"data: {json.dumps(chunk)}\n\n"
                                continue

                            elif evt_type == "error":
                                err_chunk = {
                                    "error": {
                                        "message": event.get("error", "Unknown Agent Error"),
                                        "type": "internal_server_error",
                                        "code": 500
                                    }
                                }
                                yield f"data: {json.dumps(err_chunk)}\n\n"
                                continue

                            elif evt_type == "token":
                                # Handle streaming content tokens
                                content = event.get("content", "")
                                if content:
                                    chunk = {
                                        "id": f"chatcmpl-{request_id}",
                                        "object": "chat.completion.chunk",
                                        "created": int(time.time()),
                                        "model": requested_model or "agent",
                                        "choices": [
                                            {
                                                "index": 0,
                                                "delta": {"content": content},
                                                "finish_reason": None
                                            }
                                        ]
                                    }
                                    yield f"data: {json.dumps(chunk)}\n\n"

                            elif evt_type in ["tool_start", "tool_end", "thinking_start"]:
                                # For now, skip tool events in streaming (they're not part of the response content)
                                # Could optionally emit them as custom delta fields if needed
                                continue

                            # Handle legacy content events (backward compatibility)
                            elif "content" in event:
                                content = event.get("content", "")
                                if content:
                                    chunk = {
                                        "id": f"chatcmpl-{request_id}",
                                        "object": "chat.completion.chunk",
                                        "created": int(time.time()),
                                        "model": requested_model or "agent",
                                        "choices": [
                                            {
                                                "index": 0,
                                                "delta": {"content": content},
                                                "finish_reason": None
                                            }
                                        ]
                                    }
                                    yield f"data: {json.dumps(chunk)}\n\n"
                            
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"Stream Error [{request_id}]: {e}")
                    # Try to yield error if stream is still open
                    err_chunk = {
                        "error": {"message": str(e), "type": "internal_server_error", "code": 500}
                    }
                    yield f"data: {json.dumps(err_chunk)}\n\n"
                finally:
                    state.active_requests -= 1
                    state.last_interaction_time = time.time()
                    
            return StreamingResponse(sse_wrapper(), media_type="text/event-stream")

        completion = {}
        async with log_time(f"Agent Loop [{request_id}]", level=logging.INFO, logger_override=logger):
            # Propagate skip_refinement to loop
            completion = await engine.agent_loop(
                messages,
                model=requested_model,
                request_id=request_id,
                skip_refinement=skip_refinement,
                quality_tier=quality_tier
            )

        # Phase 2: Structured Outputs - Response validation temporarily disabled
        # TODO: Re-enable after debugging response format issues
        # The fast path optimization is working, focus on that first
        logger.debug("Response validation skipped (fast path active)")

        # Update Stats
        duration_ms = (time.time() - t0_stats) * 1000
        state.request_count += 1
        state.total_response_time_ms += duration_ms

    except Exception as e:
        logger.error(f"Agent Execution Failed [{request_id}]: {e}", exc_info=True)
        state.error_count += 1
        state.last_error = str(e)
        # [DEBUG] Log the completion state
        logger.error(f"Completion state: {completion}")
        # [FIX] Don't crash the request - return graceful error response
        # Only raise HTTPException if it's already one (from FastAPI)
        if isinstance(e, HTTPException):
            raise e
        # Otherwise, return a proper error response
        return JSONResponse({
            "error": {
                "message": f"Request processing failed: {str(e)}",
                "type": "internal_server_error",
                "code": 500
            },
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"I encountered an error processing your request: {str(e)}. Please try again or contact support if the issue persists."
                },
                "finish_reason": "stop"
            }]
        }, status_code=500)
    finally:
        if not body.get("stream", False): # Streaming handles its own cleanup
            state.active_requests -= 1
            state.last_interaction_time = time.time()
    
    # [DEBUG] Temporarily return a simple response to isolate the issue
    # Phase 4: Response quality evaluation (lightweight, non-blocking)
    try:
        quality = evaluate_completion(completion)
        completion["quality"] = quality
    except Exception as eval_err:
        logger.warning(f"Quality evaluation failed: {eval_err}")

    # Return plain OpenAI-style response (no wrapper)
    return JSONResponse(completion)
