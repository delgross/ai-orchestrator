"""
System Message Push Endpoint

Allows the system to push messages directly to connected chat clients.
This enables warnings, problems, and status updates to appear in chat.

Implementation: Uses the chat endpoint to inject messages as assistant responses.
This is a simple approach that works with existing chat infrastructure.
"""
import logging
import time
import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from router.config import state, AGENT_RUNNER_URL, AGENT_RUNNER_CHAT_PATH
from router.utils import join_url

router = APIRouter(tags=["system"])
logger = logging.getLogger("router.system_messages")

class PushMessageRequest(BaseModel):
    """Request to push a system message to chat clients."""
    message: str
    message_type: str = "info"  # info, warning, error, success
    title: Optional[str] = None
    target_client_id: Optional[str] = None  # If None, sends to all active clients

@router.post("/admin/push-message")
async def push_system_message(req: PushMessageRequest):
    """
    Push a system message to connected chat clients.
    
    If target_client_id is provided, sends only to that client.
    Otherwise, sends to all active clients.
    
    Implementation: Uses the agent runner's chat endpoint to inject the message
    as an assistant response. This appears in the chat interface naturally.
    """
    if not state.clients:
        return {
            "ok": False,
            "message": "No chat clients connected",
            "sent_count": 0
        }
    
    # Determine target clients
    if req.target_client_id:
        if req.target_client_id not in state.clients:
            raise HTTPException(status_code=404, detail=f"Client {req.target_client_id} not found")
        target_clients = [req.target_client_id]
    else:
        # Send to all active clients (those seen in last 5 minutes)
        now = time.time()
        target_clients = [
            cid for cid, session in state.clients.items()
            if (now - session.last_seen) < 300  # 5 minutes
        ]
    
    if not target_clients:
        return {
            "ok": False,
            "message": "No active chat clients",
            "sent_count": 0
        }
    
    # Format message based on type
    formatted_message = _format_system_message(req.message, req.message_type, req.title)
    
    # Send message via agent runner's chat endpoint
    # This will appear as an assistant message in the chat interface
    sent_count = 0
    errors = []
    
    chat_url = join_url(AGENT_RUNNER_URL, AGENT_RUNNER_CHAT_PATH)
    
    for client_id in target_clients:
        try:
            # Use the chat endpoint to inject the message as an assistant response
            # The X-System-Message header indicates this is a system-generated message
            response = await state.client.post(
                chat_url,
                json={
                    "model": "agent:mcp",
                    "messages": [
                        {
                            "role": "system",
                            "content": formatted_message
                        },
                        {
                            "role": "assistant",
                            "content": formatted_message
                        }
                    ],
                    "stream": False
                },
                headers={
                    "Content-Type": "application/json",
                    "X-System-Message": "true",
                    "X-Client-ID": client_id  # Track which client this is for
                },
                timeout=5.0
            )
            
            if response.status_code == 200:
                logger.info(f"System message pushed to client {client_id}: {req.message_type}")
                sent_count += 1
            else:
                errors.append(f"Client {client_id}: HTTP {response.status_code}")
                logger.warning(f"Failed to push message to client {client_id}: HTTP {response.status_code}")
        except Exception as e:
            errors.append(f"Client {client_id}: {str(e)}")
            logger.warning(f"Failed to push message to client {client_id}: {e}")
    
    return {
        "ok": True,
        "sent_count": sent_count,
        "target_clients": target_clients,
        "errors": errors if errors else None
    }

def _format_system_message(message: str, message_type: str, title: Optional[str] = None) -> str:
    """Format a system message with appropriate styling."""
    icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅"
    }
    
    icon = icons.get(message_type, "ℹ️")
    
    if title:
        return f"## {icon} {title}\n\n{message}"
    else:
        return f"{icon} {message}"

