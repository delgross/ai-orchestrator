import logging
import json
import uuid
import asyncio
from typing import Dict, Any, List
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from agent_runner.agent_runner import get_shared_state, get_shared_engine
from agent_runner.mcp_server.transport import SSEServerTransport
from agent_runner.mcp_server.interceptors import (
    ToolInterceptor, WriteOwnInterceptor, PrivacyInterceptor, LoggingInterceptor
)

logger = logging.getLogger("agent_runner.mcp_server.router")
router = APIRouter()
transport = SSEServerTransport()

# --- Interceptor Stack ---
interceptors: List[ToolInterceptor] = [
    LoggingInterceptor(),
    WriteOwnInterceptor(),
    PrivacyInterceptor()
]

# --- Auth Helper ---
def verify_auth(request: Request):
    state = get_shared_state()
    token = state.router_auth_token
    auth_header = request.headers.get("Authorization", "")
    
    if not token: return # Dev/Open Mode check (Plan says Secure, usually enforced)
    
    if not auth_header.startswith("Bearer ") or auth_header[7:] != token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid Router Auth Token")

# --- Endpoints ---

@router.get("/mcp/sse")
async def mcp_sse_endpoint(request: Request):
    verify_auth(request)
    client_name = request.headers.get("X-Client-Name", "unknown")
    session = transport.create_session(client_name)
    return StreamingResponse(transport.sse_generator(session, request), media_type="text/event-stream")

@router.post("/mcp/messages")
async def mcp_messages_endpoint(request: Request):
    verify_auth(request)
    session_id = request.query_params.get("session_id")
    session = transport.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        payload = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    # Fire and forget processing
    asyncio.create_task(process_message(session, payload))
    return Response(status_code=202)

# --- Message Processing ---

async def process_message(session, message: Dict[str, Any]):
    try:
        method = message.get("method")
        msg_id = message.get("id")
        
        engine = get_shared_engine()
        response = None
        
        print(f"DEBUG: Processing method {method} for session {session.session_id}")
        
        # Context for Interceptors
        context = {
            "client_name": session.client_name,
            "session_id": session.session_id
        }

        if method == "initialize":
            params = message.get("params", {})
            client_info = params.get("clientInfo", {})
            capabilities = params.get("capabilities", {})
            
            # Store context in session
            session.client_info = client_info
            session.client_capabilities = capabilities
            
            # Update client name if provided (more accurate than header)
            if "name" in client_info:
                session.client_name = client_info["name"]
                
            logger.info(f"[MCP] Initialized session {session.session_id} for client '{session.client_name}' (v{client_info.get('version', 'unknown')})")
            logger.info(f"[MCP] Client Capabilities: {json.dumps(capabilities)}")

            response = _make_rpc_response(msg_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}, 
                    "prompts": {},
                    "resources": {} # Advertise Resource Support
                },
                "serverInfo": {"name": "Antigravity", "version": "1.0.0"}
            })

        elif method == "notifications/initialized":
            return 

        elif method == "tools/list":
            # Aggregation (Proxy Internal Engine)
            # engine.get_all_tools() now returns EVERYTHING when called without messages
            all_tools = await engine.get_all_tools()
            
            # Format engine-style tools back to MCP schema
            mcp_tools = [_format_tool_to_mcp(t) for t in all_tools]
            
            # Re-inject 'ask_antigravity' Meta-Tool (Phase 14 Agentic Bridge)
            mcp_tools.append({
                "name": "ask_antigravity",
                "description": "Delegate a complex goal to the full Antigravity reasoning loop. Use this for deep research, multi-step coding, or system-wide analysis.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "goal": {"type": "string", "description": "The high-level goal or problem to solve"},
                        "context": {"type": "string", "description": "Optional context or constraints"}
                    },
                    "required": ["goal"]
                }
            })
            
            response = _make_rpc_response(msg_id, {"tools": mcp_tools})
        
        elif method == "resources/list":
            # Expose Memory Banks as Resources
            from agent_runner.memory_server import MemoryServer
            # Note: Ideally we instance once or use shared, but this is stateless http wrapper:
            mem = MemoryServer()
            banks_res = await mem.list_memory_banks()
            resources = []
            
            if banks_res.get("ok"):
                for bank in banks_res.get("banks", []):
                    # Filter private banks? Or list them but block read?
                    # Generally listing is safe-ish, but let's respect privacy if we can.
                    # For now list all, PrivacyInterceptor blocks reads.
                    kb_id = bank.get("kb_id")
                    resources.append({
                        "uri": f"memory://{kb_id}/summary",
                        "name": f"Memory Bank: {kb_id}",
                        "description": f"Summary and stats for the {kb_id} knowledge base.",
                        "mimeType": "text/markdown"
                    })
            
            # Expose System Logs
            resources.append({
                "uri": "system://logs/tail",
                "name": "System Logs (Tail)",
                "description": "The last 50 lines of the Agent Runner logs.",
                "mimeType": "text/plain"
            })
            
            response = _make_rpc_response(msg_id, {"resources": resources})

        elif method == "resources/read":
            params = message.get("params", {})
            uri = params.get("uri")
            
            # 1. Run Interceptors (Privacy Check via PrivacyInterceptor)
            # Create synthetic tool callArgs for the interceptor
            args = {"uri": uri}
            try:
                for ic in interceptors:
                     await ic.before_execution("read_resource", args, context)
            except Exception as e:
                # Blocked by interceptor
                raise Exception(str(e))
            
            content = ""
            
            if uri.startswith("memory://"):
                # Parse kb_id
                import re
                match = re.match(r"memory://([^/]+)/summary", uri)
                if match:
                    kb_id = match.group(1)
                    
                    # [Removed Inline Check - Moved to PrivacyInterceptor]
                    
                    from agent_runner.registry import ServiceRegistry
                    # We need the memory server just to fetch data now, not for auth
                    mem = ServiceRegistry.get_memory_server()
                    if mem:
                         cfg_res = await mem.get_bank_config(kb_id)
                         content = f"# Memory Bank: {kb_id}\n\n"
                         if cfg_res.get("ok"):
                             config = cfg_res.get("config", {})
                             content += f"Owner: {config.get('owner')}\n"
                             content += f"Created: {config.get('created_at')}\n"

                        
            elif uri == "system://logs/tail":
                # Read log file
                try:
                    from agent_runner.config import PROJECT_ROOT
                    log_path = os.path.join(PROJECT_ROOT, "logs", "agent_runner.log")
                    if os.path.exists(log_path):
                        # Tail last 2KB
                        with open(log_path, "rb") as f:
                            f.seek(0, 2)
                            fsize = f.tell()
                            f.seek(max(fsize - 4096, 0), 0)
                            content = f.read().decode("utf-8", errors="replace")
                except Exception as e:
                    content = f"Error reading logs: {e}"
            
            response = _make_rpc_response(msg_id, {
                "contents": [{
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": content
                }]
            })
        elif method == "prompts/list":
            # [Phase 14] Dynamic Prompts
            prompts = []
            
            # 1. Delegate Task (Always available)
            prompts.append({
                "name": "delegate_task",
                "description": "Delegate a complex goal to the Antigravity Agent.",
                "arguments": [
                    {"name": "goal", "description": "The goal to achieve", "required": True},
                    {"name": "context", "description": "Additional context", "required": False}
                ]
            })
            
            # 2. Client-Specific Prompts
            if session.client_name == "Cursor":
                prompts.append({
                    "name": "explain_architecture", 
                    "description": "Ask Antigravity to explain the system architecture.",
                    "arguments": []
                })

            response = _make_rpc_response(msg_id, {"prompts": prompts})
            
            # 3. Resource Prompts
            prompts.append({
                "name": "summarize_resource",
                "description": "Read a resource and summarize its content.",
                "arguments": [
                    {"name": "uri", "description": "The URI of the resource", "required": True}
                ]
            })

        elif method == "prompts/get":
            params = message.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            
            messages = []
            if name == "delegate_task":
                goal = args.get("goal", "Fix this.")
                ctx = args.get("context", "")
                messages.append({
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Please perform the following goal using your agentic capabilities:\n\nGOAL: {goal}\nCONTEXT: {ctx}\n\nUse the `ask_antigravity` tool to execute this."
                    }
                })
            elif name == "explain_architecture":
                 messages.append({
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "Please explain the high-level system architecture based on your internal memory banks. Use `ask_antigravity` to allow deep research if needed."
                    }
                })

            elif name == "summarize_resource":
                uri = args.get("uri")
                messages.append({
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Please read the resource at `{uri}` and provide a concise summary of its contents.\n\nUse the `read_resource` tool (or internal equivalent) to fetch it."
                    }
                })
                
            response = _make_rpc_response(msg_id, {"messages": messages})

        elif method == "tools/call":
            params = message.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            
            # 1. Before Execution Interceptors
            try:
                for ic in interceptors:
                    args = await ic.before_execution(name, args, context)
            except Exception as e:
                # Interceptor blocked it
                await session.send_message(_make_rpc_error(msg_id, -32003, str(e)))
                return

            # [Phase 14] Intercept 'ask_antigravity' Meta-Tool
            if name == "ask_antigravity":
                goal = args.get("goal")
                user_context = args.get("context", "")
                full_prompt = f"Goal: {goal}\nContext: {user_context}"
                
                logger.info(f"[MCP] Delegating goal to Agent: {goal}")
                
                # Run the Agent Loop
                from agent_runner.agent_runner import _agent_loop
                
                try:
                    # Run Loop
                    # Note: We pass NO tools to let it auto-discover the Engine's tools (recursion!)
                    result = await _agent_loop(
                        messages=[{"role": "user", "content": full_prompt}]
                    )
                    
                    # Extract final answer
                    # The loop returns the final message content
                    # We assume _agent_loop returns the full response dict.
                    output_text = "(No output)"
                    if isinstance(result, dict):
                         # Usually returns {'role': 'assistant', 'content': ...}
                         output_text = result.get("content", str(result))
                    else:
                        output_text = str(result)
                    
                    response = _make_rpc_response(msg_id, {
                        "content": [{"type": "text", "text": output_text}]
                    })
                except Exception as e:
                     logger.error(f"[MCP] Agent Delegation Failed: {e}", exc_info=True)
                     response = _make_rpc_error(msg_id, -32000, f"Agent Delegation Failed: {e}")
                
                # Send response and return (Skip standard execution)
                await session.send_message(response)
                return

            # 2. Execution
            engine_tool_call = {
                "function": {"name": name, "arguments": json.dumps(args)},
                "id": str(uuid.uuid4()), "type": "function"
            }
            try:
                raw_result = await engine.execute_tool_call(engine_tool_call)
                
                # 3. After Execution Interceptors
                for ic in interceptors:
                    raw_result = await ic.after_execution(name, raw_result, context)
                
                # Format Result
                output_text = _format_result(raw_result)
                response = _make_rpc_response(msg_id, {
                    "content": [{"type": "text", "text": output_text}]
                })
            except Exception as e:
                response = _make_rpc_error(msg_id, -32000, str(e))

        elif method == "ping":
            response = _make_rpc_response(msg_id, {})

        elif method == "debug/session":
            # [Debug Tool] Verify we captured client info
            response = _make_rpc_response(msg_id, {
                "client_name": session.client_name,
                "client_info": session.client_info,
                "capabilities": session.client_capabilities
            })
            
        else:
            response = _make_rpc_error(msg_id, -32601, "Method not found")

        if response:
            await session.send_message(response)

    except Exception as e:
        logger.error(f"MCP Process Error: {e}")
        # best effort error
        # session might be closed/dead
        pass

# --- Helpers ---

def _make_rpc_response(msg_id, result):
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}

def _make_rpc_error(msg_id, code, message):
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}

def _format_result(res):
    if isinstance(res, dict):
        if "result" in res: return json.dumps(res["result"])
        if "error" in res: return json.dumps(res)
        return json.dumps(res)
    return str(res)

def _format_tool_to_mcp(engine_tool: Dict[str, Any]) -> Dict[str, Any]:
    """Convert OpenAI-style tool definition back to MCP format."""
    fn = engine_tool.get("function", {})
    return {
        "name": fn.get("name"),
        "description": fn.get("description"),
        "inputSchema": fn.get("parameters", {"type": "object", "properties": {}})
    }
