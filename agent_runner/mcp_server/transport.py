import logging
import json
import asyncio
from typing import Dict, Any, Optional
from uuid import uuid4
from fastapi import Request

logger = logging.getLogger("agent_runner.mcp_server.transport")

class MCPSession:
    def __init__(self, session_id: str, client_name: str):
        self.session_id = session_id
        self.client_name = client_name
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.active = True
        self.client_info: Dict[str, Any] = {}
        self.client_capabilities: Dict[str, Any] = {}

    async def send_message(self, message: Dict[str, Any]):
        """Queue a JSON-RPC message to be sent via SSE."""
        if self.active:
            await self.event_queue.put(message)

    async def close(self):
        """Close the session."""
        self.active = False
        await self.event_queue.put(None) # Signal end

class SSEServerTransport:
    def __init__(self):
        self.sessions: Dict[str, MCPSession] = {}

    def create_session(self, client_name: str) -> MCPSession:
        session_id = str(uuid4())
        session = MCPSession(session_id, client_name)
        self.sessions[session_id] = session
        logger.info(f"[Transport] Created Session {session_id} for client '{client_name}'")
        return session

    def get_session(self, session_id: str) -> Optional[MCPSession]:
        return self.sessions.get(session_id)

    def close_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"[Transport] Closed Session {session_id}")

    async def sse_generator(self, session: MCPSession, request: Request):
        try:
            # Yield "endpoint" event immediately
            base_url = str(request.base_url).rstrip("/")
            endpoint_event = {
                "type": "endpoint", 
                "uri": f"{base_url}/mcp/messages?session_id={session.session_id}"
            }
            yield f"event: endpoint\ndata: {json.dumps(endpoint_event)}\n\n"
            
            while True:
                message = await session.event_queue.get()
                if message is None: break
                yield f"event: message\ndata: {json.dumps(message)}\n\n"
        except asyncio.CancelledError:
            logger.info(f"[Transport] Client disconnected: {session.session_id}")
        finally:
            self.close_session(session.session_id)
