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

    # Initialize variables to prevent UnboundLocalError
    completion = {}
    t0_stats = time.time()

    # Use the engine to process the request
    state.active_requests += 1

    stream_mode = body.get("stream", False)
    requested_model = body.get(OBJ_MODEL)

    # Prevent infinite recursion / invalid model names
    if requested_model == "agent:mcp" or not requested_model or ":" not in requested_model:
        requested_model = None

    logger.info(f"REQ [{request_id}] Agent Execution: Model='{requested_model}' Stream={stream_mode} SkipRefinement={skip_refinement}")

    # Extract the raw user input (last message) for trigger check
    last_msg = messages[-1].get("content") if messages else ""

    try:
        if stream_mode:
            async def sse_wrapper():
                try:
                    async with log_time(f"Agent Stream [{request_id}]", level=logging.INFO, logger_override=logger):
                        # Propagate skip_refinement to stream

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

                        # [PHASE 60.5] GENERIC FAST LANE (Auto-Execute) for Streaming
                        fast_lane_activated = False
                        try:
                            # 1. Classify Intent
                            intent_res = await engine._classify_search_intent(last_msg)
                            auto_exec = intent_res.get("auto_execute")

                            if auto_exec and isinstance(auto_exec, dict):
                                tool_name = auto_exec.get("tool")
                                tool_args = auto_exec.get("args", {})

                                # [FIX] Prevent execution of None/null tools (Maître d' hallucination)
                                if not tool_name or str(tool_name).lower() == "none":
                                    logger.warning(f"Fast Lane skipped: Invalid tool name '{tool_name}' in auto_execute.")
                                    raise ValueError("Fast Lane Abort: Invalid tool name")

                                logger.info(f"🚀 STREAMING FAST LANE: Auto-Executing '{tool_name}'")

                                # 2. Execute Immediate Tool
                                fake_tool_call = {
                                    "function": {
                                        "name": tool_name,
                                        "arguments": json.dumps(tool_args)
                                    },
                                    "id": f"fast-{uuid.uuid4()}"
                                }
                                tool_result = await engine.execute_tool_call(fake_tool_call, request_id)

                                # Convert result to streaming format
                                content = "Done."
                                if "output" in tool_result:
                                    content = tool_result["output"]
                                elif "result" in tool_result:
                                    res = tool_result["result"]
                                    if isinstance(res, dict):
                                        # Smart formatting for common tools
                                        if "time" in res:
                                            content = f"The current time is {res['time']}."
                                        elif "weather" in res:
                                            content = json.dumps(res, indent=2)
                                        else:
                                            content = json.dumps(res, indent=2)
                                    else:
                                        content = str(res)
                                elif "error" in tool_result:
                                    content = f"Error: {tool_result['error']}"

                                # Stream the result
                                yield f"data: {json.dumps({'id': f'chatcmpl-{request_id}', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': requested_model or 'agent', 'choices': [{'index': 0, 'delta': {'content': content}, 'finish_reason': 'stop'}]})}\n\n"
                                yield f"data: {json.dumps({'id': f'chatcmpl-{request_id}', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': requested_model or 'agent', 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"

                        except Exception as fast_err:
                            logger.warning(f"Fast Lane Failed: {fast_err}. Falling back to Agent.")
                            # Continue to normal streaming flow

                        if not fast_lane_activated:
                            async for event in engine.nexus.dispatch(
                                user_message=last_msg,
                                request_id=request_id,
                                context=messages[:-1] # Nexus rebuilds context
                            ):
                                evt_type = event.get("type")

                                try:
                                    evt_type = event.get("type")
                                except Exception as e:
                                    logger.error(f"Malformed event in stream [{request_id}]: {e}, event: {event}")
                                    continue

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
                                        logger.debug(f"Sending token chunk: {content[:50]}...")
                                        yield f"data: {json.dumps(chunk)}\n\n"

                                elif evt_type == "control_ui":
                                    # Stream custom control events to the frontend
                                    # The frontend should handle these "control" deltas specifically
                                    chunk = {
                                        "id": f"chatcmpl-{request_id}",
                                        "object": "chat.completion.chunk",
                                        "created": int(time.time()),
                                        "model": requested_model or "agent",
                                        "choices": [
                                            {
                                                "index": 0,
                                                "delta": {
                                                    "control": {
                                                        "type": "ui",
                                                        "target": event.get("target"),
                                                        "action": "open"
                                                    }
                                                },
                                                "finish_reason": None
                                            }
                                        ]
                                    }
                                    yield f"data: {json.dumps(chunk)}\n\n"

                                elif evt_type in ["tool_start", "thinking_start"]:
                                    # Skip tool start events
                                    continue

                                elif evt_type == "tool_end":
                                    # [FIX] Allow Sovereign Triggers (Nexus Diagnostic Tools) to separate their output
                                    if event.get("tool") == "nexus_trigger":
                                        content = event.get("output", "")
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
                                    else:
                                        # Hide standard internal tool outputs
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
            return StreamingResponse(sse_wrapper(), media_type="text/event-stream")

        # [CRITICAL FIX] Apply Nexus trigger checking to NON-STREAMING requests too
        # The Nexus was only used for streaming, causing triggers to be bypassed for regular completions
        logger.warning(f"NON-STREAMING REQUEST [{request_id}]: Checking Nexus triggers for: '{last_msg[:50]}...'")
        trigger_result = await engine.nexus._check_and_execute_trigger(last_msg)

        if trigger_result:
            logger.warning(f"NON-STREAMING TRIGGER ACTIVATED [{request_id}]: {trigger_result.get('name', 'unknown')}")
            # Convert trigger result to OpenAI completion format
            completion = {
                "id": f"chatcmpl-{request_id}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": requested_model or "agent",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": trigger_result.get("output", "Trigger executed successfully")
                    },
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }

        # [PHASE 60.5] GENERIC FAST LANE (Auto-Execute)
        # Check if Maître d' recommended an immediate execution
        # We need to peek at the intent classification result.
        # This requires moving the classification UP into the route or exposing a helper.
        # For now, we will trust the Nexus dispatch to handle this if we extended Nexus.
        # BUT, Nexus typically returns events.
        # Let's check ONLY if we aren't streaming, or if streaming is handled above.

        # Wait, the Nexus Dispatch above ONLY ran for stream=True.
        # We need to run intent classification explicitly for non-streaming if we want Fast Lane there too.
        # Actually, let's keep it simple: reliable Fast Lane works best with Streaming.
        # But if the user didn't request streaming, we still want speed.

        # Let's perform a lightweight Intent Check here if no trigger happened
        elif not trigger_result:
            # Fast Lane Check
            try:
                # Classification happens here
                intent_res = await engine._classify_search_intent(last_msg)
                auto_exec = intent_res.get("auto_execute")

                if auto_exec and isinstance(auto_exec, dict):
                    tool_name = auto_exec.get("tool")
                    tool_args = auto_exec.get("args", {})
                    logger.info(f"🚀 FAST LANE ACTIVATED: Auto-Executing '{tool_name}'")

                    # Execute Tool
                    # We need to find the tool definition or just run it via executor
                    # Executor 'execute_tool_call' expects a tool_call dict
                    fake_tool_call = {
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(tool_args)
                        },
                        "id": f"fast-{uuid.uuid4()}"
                    }

                    tool_result = await engine.execute_tool_call(fake_tool_call, request_id)

                    # Format output naturally [FIXED output extraction]
                    final_output = "Done."
                    if "output" in tool_result:
                        final_output = tool_result["output"]
                    elif "result" in tool_result:
                        res = tool_result["result"]
                        if isinstance(res, dict):
                            # Smart formatting for common tools
                            if "time" in res:
                                final_output = f"The current time is {res['time']}."
                            elif "weather" in res:
                                final_output = json.dumps(res, indent=2)
                            else:
                                final_output = json.dumps(res, indent=2)
                        else:
                            final_output = str(res)
                    elif "error" in tool_result:
                        final_output = f"Error: {tool_result['error']}"

                    # Return Synthetic System Response
                    completion = {
                        "id": f"fast-{request_id}",
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "model": "fast-lane",
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": final_output
                            },
                            "finish_reason": "stop"
                        }],
                        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                    }
            except Exception as fast_err:
                logger.warning(f"Fast Lane Failed: {fast_err}. Falling back to Agent.")
                completion = {} # proceed to normal loop

        if not completion:
            logger.warning(f"NON-STREAMING NO TRIGGER [{request_id}]: Proceeding to agent loop")
            completion = {}
            async with log_time(f"Agent Loop [{request_id}]", level=logging.INFO, logger_override=logger):
                # Propagate skip_refinement to loop
                try:
                    completion = await engine.agent_loop(
                        messages,
                        model=requested_model,
                        request_id=request_id,
                        skip_refinement=skip_refinement,
                        quality_tier=quality_tier
                    )
                    logger.info(f"Agent loop completed successfully. Completion keys: {list(completion.keys()) if isinstance(completion, dict) else type(completion)}")
                    if isinstance(completion, dict) and "metadata" in completion:
                        logger.warning(f"AGENT: Response contains 'metadata' field with hallucination_detection: {completion.get('metadata', {}).get('hallucination_detection', {}).get('is_hallucination', 'unknown')}")
                except Exception as loop_e:
                    logger.error(f"Agent loop failed: {loop_e}", exc_info=True)
                    raise

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

    return completion

@router.get("/test")
async def test_route():
    print(f"DEBUG: Test route called")
    return {"test": "ok"}
