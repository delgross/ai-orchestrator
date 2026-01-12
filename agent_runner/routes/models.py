import time
from typing import List, Dict, Any
from fastapi import APIRouter
from common.constants import OBJ_LIST, OBJ_MODEL
from agent_runner.agent_runner import get_shared_state

router = APIRouter()

@router.get("/models")
async def get_models():
    """Return available Agent models/roles."""
    state = get_shared_state()
    data = []
    now = int(time.time())

    def make_model(id: str, owner: str):
        return {
            "id": id,
            "object": OBJ_MODEL,
            "created": now,
            "owned_by": owner,
            "permission": [],
            "root": id,
            "parent": None
        }

    # 1. The Main Agent
    data.append(make_model("agent:mcp", "agent_runner"))
    
    # 2. Configured Personas
    if state and state.config:
        personas = state.config.get("personas", {})
        for key, persona in personas.items():
            name = f"agent:{key}"
            data.append(make_model(name, "agent_runner"))

    # 3. The Underlying Model (True Sovereign)
    if state:
        agent_model = state.agent_model  # "ollama:llama3.3:70b"
        data.append(make_model(agent_model, "system"))

    return {"object": OBJ_LIST, "data": data}
