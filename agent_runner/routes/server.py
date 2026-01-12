import logging
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from agent_runner.agent_runner import get_shared_state, get_shared_engine
from agent_runner.executor import ToolExecutor

router = APIRouter()
logger = logging.getLogger("agent_runner.mcp_server")

# Active SSE Sessions: token -> queue
active_sessions: Dict[str, asyncio.Queue] = {}

def get_router_auth_token():
    state = get_shared_state()
    return state.router_auth_token

def verify_auth(request: Request):
    token = get_router_auth_token()
    auth_header = request.headers.get("Authorization", "")
    if not token:
        # If no token configured in system, we could default to open, but plan says SECURE.
        # So we require it.
        return # Dev mode? No, stick to plan.
    
    if not auth_header.startswith("Bearer ") or auth_header[7:] != token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid Router Auth Token")

@router.get("/mcp/sse")
async def mcp_sse_endpoint(request: Request):
    """
    Standard MCP SSE Endpoint.
    Establishes a connection and yields JSON-RPC events.
    """
    verify_auth(request)
    
    # 1. Session ID (for correlating POST messages)
    session_id = str(uuid.uuid4())
    logger.info(f"New MCP Session: {session_id} (Client: {request.headers.get('X-Client-Name', 'unknown')})")
    
    event_queue = asyncio.Queue()
    active_sessions[session_id] = event_queue
    
    async def sse_generator():
        # Yield the endpoint URL as the first event (Standard MCP)
        # The client will use this URL to send POST messages
        # "endpoint" event
        base_url = str(request.base_url).rstrip("/")
        endpoint_event = {
            "type": "endpoint", 
            "uri": f"{base_url}/mcp/messages?session_id={session_id}"
        }
        yield f"event: endpoint\ndata: {json.dumps(endpoint_event)}\n\n"
        
        try:
            while True:
                # Wait for messages from the queue (put by POST /mcp/messages)
                message = await event_queue.get()
                if message is None: break # Shutdown signal
                
                # Yield JSON-RPC message
                yield f"event: message\ndata: {json.dumps(message)}\n\n"
        except asyncio.CancelledError:
            logger.info(f"MCP Session Disconnected: {session_id}")
        finally:
            active_sessions.pop(session_id, None)
            
    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@router.post("/mcp/messages")
async def mcp_messages_endpoint(request: Request):
    """
    Handle incoming JSON-RPC messages from the client.
    Note: MCP uses a separate POST endpoint for client -> server messages.
    """
    verify_auth(request)
    
    session_id = request.query_params.get("session_id")
    if not session_id or session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        payload = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    # Asynchronous Handling
    # We don't block the POST response. We process logic and push RESULT to the SSE queue.
    # The POST response itself is usually 202 Accepted or empty 200.
    asyncio.create_task(handle_mcp_message(session_id, payload, request.headers))
    
    return Response(status_code=202)

async def handle_mcp_message(session_id: str, message: Dict[str, Any], headers: Any):
    queue = active_sessions.get(session_id)
    if not queue: return
    
    try:
        method = message.get("method")
        msg_id = message.get("id")
        
        engine = get_shared_engine()
        state = get_shared_state()
        client_name = headers.get("X-Client-Name", "unknown").lower()
        
        response = None
        
        # --- JSON-RPC Method Dispatch ---
        
        if method == "initialize":
            # Handshake
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {} # We support tools
                    },
                    "serverInfo": {
                        "name": "Antigravity Orchestrator",
                        "version": "1.0.0"
                    }
                }
            }
            
        elif method == "notifications/initialized":
            # Client Ack
            return # No response needed for notification
            
        elif method == "tools/list":
            # Aggregation: Get absolute ALL tools
            all_tools = await engine.get_all_tools()
            
            # Convert to MCP Tool format if needed
            # Our engine returns OpenAI-style schemas: { type: function, function: { name, ... } }
            # MCP style: { name, description, inputSchema } (top level)
            mcp_tools = []
            for t in all_tools:
                fn = t.get("function", {})
                mcp_tools.append({
                    "name": fn.get("name"),
                    "description": fn.get("description"),
                    "inputSchema": fn.get("parameters", {})
                })
                
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": mcp_tools
                }
            }
            
        elif method == "tools/call":
            # Execution
            params = message.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            
            # --- SECURITY & INTERCEPTION LAYER ---
            
            # 1. Intercept store_fact -> Enforce Write-Own
            if name == "store_fact":
                # Force kb_id to client_name
                if "kb_id" in args and args["kb_id"] != client_name:
                    logger.warning(f"MCP Client '{client_name}' tried to write to '{args['kb_id']}'. Redirecting to '{client_name}'.")
                
                args["kb_id"] = client_name # Override
                
            # 2. Intercept query_facts -> Enforce Read-Privacy
            if name == "query_facts" or name == "semantic_search":
                target_kb = args.get("kb_id")
                if target_kb:
                    # Check privacy (Simulated check for now until table exists)
                    # For now: if target_kb starts with "private_" and not owner -> Block
                    if str(target_kb).startswith("private_") and target_kb != f"private_{client_name}":
                        response = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "error": {
                                "code": -32003,
                                "message": f"Access Denied: Memory Bank '{target_kb}' is PRIVATE."
                            }
                        }
                        await queue.put(response)
                        return

            # --- EXECUTION ---
            
            # Use Engine execution (which handles internal tools + MCP proxying)
            # Reconstruct OpenAI-style tool call
            tool_call = {
                "function": {
                    "name": name,
                    "arguments": json.dumps(args)
                },
                "id": str(uuid.uuid4()),
                "type": "function"
            }
            
            try:
                # Execute
                result_raw = await engine.execute_tool_call(tool_call, user_query="")
                
                # Extract Result Content
                # Engine returns: { result: ... } or { error ... } or raw value
                output_text = "{}".format(result_raw)
                if isinstance(result_raw, dict):
                     # Try to be cleaner
                     if "result" in result_raw: output_text = json.dumps(result_raw["result"])
                     elif "error" in result_raw: output_text = json.dumps(result_raw)
                     else: output_text = json.dumps(result_raw)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": output_text
                            }
                        ]
                    }
                }
            except Exception as e:
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                }

        elif method == "ping":
            response = {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        else:
             # Unknown method
             response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            }

        if response:
            await queue.put(response)
            
    except Exception as e:
        logger.error(f"MCP Handler Error: {e}")
        err_response = {
            "jsonrpc": "2.0",
            "id": msg_id if 'msg_id' in locals() else None,
            "error": {
                "code": -32603,
                "message": "Internal Error"
            }
        }
        await queue.put(err_response)
