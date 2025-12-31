import logging
import json
import time
import uuid
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from common.constants import OBJ_CHAT_COMPLETION, OBJ_MODEL
from common.logging_utils import log_time
from agent_runner.agent_runner import get_shared_state, get_shared_engine

router = APIRouter()
logger = logging.getLogger("agent_runner.chat")

@router.post("/v1/chat/completions")
async def chat_completions(body: Dict[str, Any], request: Request):
    state = get_shared_state()
    engine = get_shared_engine()
    
    messages = body.get("messages", [])
    if not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="messages must be a list")
    
    # Extract Request ID for distributed tracing
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())[:8]

    # Use the engine to process the request
    state.active_requests += 1
    state.last_interaction_time = time.time()
    
    # Timer for stats endpoint (distinct from log_time)
    t0_stats = time.time()
    
    try:
        requested_model = body.get(OBJ_MODEL)
        stream_mode = body.get("stream", False)
        
        logger.info(f"REQ [{request_id}] Agent Execution: Model='{requested_model}' Stream={stream_mode}")

        # Prevent infinite recursion / invalid model names
        if requested_model == "agent:mcp" or not requested_model or ":" not in requested_model:
            requested_model = None
            
        if stream_mode:
            async def sse_wrapper():
                try:
                    async with log_time(f"Agent Stream [{request_id}]", level=logging.INFO, logger_override=logger):
                        async for event in engine.agent_stream(messages, model=requested_model, request_id=request_id):
                            # Wrap in OpenAI-compatible chunk
                            chunk = {
                                "id": f"chatcmpl-{request_id}",
                                "object": "chat.completion.chunk",
                                "created": int(time.time()),
                                "model": requested_model or "agent",
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": event, # Inject custom event fields into delta
                                        "finish_reason": None
                                    }
                                ]
                            }
                            # Special handling for 'done' event? 
                            if event.get("type") == "done":
                                chunk["choices"][0]["delta"] = {}
                                chunk["choices"][0]["finish_reason"] = event.get("stop_reason", "stop")
                                if "usage" in event: chunk["usage"] = event["usage"]

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
            completion = await engine.agent_loop(messages, model=requested_model, request_id=request_id)
        
        # Update Stats
        duration_ms = (time.time() - t0_stats) * 1000
        state.request_count += 1
        state.total_response_time_ms += duration_ms

    except Exception as e:
        logger.error(f"Agent Execution Failed [{request_id}]: {e}", exc_info=True)
        state.error_count += 1
        state.last_error = str(e)
        raise e
    finally:
        if not body.get("stream", False): # Streaming handles its own cleanup
            state.active_requests -= 1
            state.last_interaction_time = time.time()
    
    completion[OBJ_MODEL] = body.get(OBJ_MODEL, "agent:mcp")
    completion.setdefault("created", int(time.time()))
    completion.setdefault("object", OBJ_CHAT_COMPLETION)
    completion.setdefault("id", f"chatcmpl-{int(time.time() * 1000)}")
    
    return JSONResponse(completion)
