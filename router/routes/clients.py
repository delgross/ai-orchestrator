import logging
import time
import uuid
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import BaseModel

from agent_runner.agent_runner import get_shared_state
from agent_runner.state import ClientSession

router = APIRouter()
logger = logging.getLogger("agent_runner.clients")

class RegisterClientRequest(BaseModel):
    name: str
    capabilities: List[str] = []
    priority: int = 1 # 0=Observer, 1=Standard, 2=Primary
    metadata: dict = {}

class HeartbeatRequest(BaseModel):
    client_id: str
    session_token: str # Security (Future) - currently just validated for existence

@router.post("/clients/register")
async def register_client(req: RegisterClientRequest):
    """Register a new dashboard/client session."""
    state = get_shared_state()
    
    # Generate ID
    client_id = f"client_{uuid.uuid4().hex[:8]}"
    session_token = uuid.uuid4().hex # Simple token for ensuring ownership
    
    now = time.time()
    
    session = ClientSession(
        client_id=client_id,
        name=req.name,
        capabilities=req.capabilities,
        priority=req.priority,
        first_seen=now,
        last_seen=now,
        metadata={**req.metadata, "session_token": session_token}
    )
    
    state.clients[client_id] = session
    
    logger.info(f"Client Registered: {req.name} ({client_id})")
    
    # Auto-focus if this is the first primary client
    if req.priority >= 1 and state.active_client_id is None:
        state.active_client_id = client_id
        logger.info(f"Auto-focused client: {client_id}")

    return {
        "ok": True,
        "client_id": client_id,
        "session_token": session_token,
        "message": "Welcome to the Antigravity Registry"
    }

@router.post("/clients/heartbeat")
async def client_heartbeat(req: HeartbeatRequest):
    """Update last_seen timestamp."""
    state = get_shared_state()
    
    if req.client_id not in state.clients:
        return {"ok": False, "error": "Client not found. Please re-register."}
    
    session = state.clients[req.client_id]
    
    # Validate Token (Simple Check)
    if session.metadata.get("session_token") != req.session_token:
        logger.warning(f"Security Alert: Heartbeat token mismatch for {req.client_id}")
        return {"ok": False, "error": "Invalid session token"}
        
    session.last_seen = time.time()
    return {"ok": True}

@router.get("/clients/list")
async def list_clients():
    """List connected clients for visibility."""
    state = get_shared_state()
    
    # Convert to list for JSON response
    roster = []
    for cid, session in state.clients.items():
        # Don't leak session_token in public list
        safe_meta = session.metadata.copy()
        safe_meta.pop("session_token", None)
        
        roster.append({
            "client_id": session.client_id,
            "name": session.name,
            "capabilities": session.capabilities,
            "priority": session.priority,
            "connected_s": round(time.time() - session.first_seen),
            "idle_s": round(time.time() - session.last_seen),
            "is_active": (cid == state.active_client_id),
            "metadata": safe_meta
        })
        
    return {
        "ok": True,
        "count": len(roster),
        "active_client_id": state.active_client_id,
        "clients": roster
    }
