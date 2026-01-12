"""
Compatibility shim for agent_runner module.
Provides legacy constants and functions after refactoring.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from agent_runner.state import AgentState
from agent_runner.engine import AgentEngine

logger = logging.getLogger("agent_runner.shim")

# Legacy Constants
TASK_MODEL = os.getenv("TASK_MODEL", "ollama:llama3.3:70b-instruct-q8_0")
AGENT_MODEL = os.getenv("AGENT_MODEL", "ollama:llama3.3:70b-instruct-q8_0")

# Legacy global state (initialized on first use)
from agent_runner.service_registry import ServiceRegistry

_shared_state: Optional[AgentState] = None
_shared_engine: Optional[AgentEngine] = None

def get_shared_state() -> AgentState:
    global _shared_state
    if _shared_state is None:
        try:
            # Try getting from registry first to prefer explicit registration
            _shared_state = ServiceRegistry.get_state()
        except RuntimeError:
            _shared_state = AgentState()
            ServiceRegistry.register_state(_shared_state)
    return _shared_state

def get_shared_engine() -> AgentEngine:
    global _shared_engine
    if _shared_engine is None:
        try:
            _shared_engine = ServiceRegistry.get_engine()
        except RuntimeError:
            _shared_engine = AgentEngine(get_shared_state())
            ServiceRegistry.register_engine(_shared_engine)
    return _shared_engine

async def _agent_loop(user_messages: List[Dict[str, Any]], model: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, skip_refinement: bool = False) -> Dict[str, Any]:
    """Compatibility wrapper for engine.agent_loop."""
    engine = get_shared_engine()
    return await engine.agent_loop(user_messages, model=model, tools=tools, skip_refinement=skip_refinement)

# Deprecated: Tool definitions have migrated to engine.py
# MCP_TOOLS and FILE_TOOLS removed to avoid duplication.
