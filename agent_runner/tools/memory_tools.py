import logging
import json
from typing import Dict, Any, List, Optional
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner")

async def tool_memory_store_fact(state: AgentState, content: str, category: str = "general", confidence: float = 1.0) -> Dict[str, Any]:
    """
    Store a fact in the agent's long-term memory.
    Use this to remember user preferences, important details, or context for future conversations.
    """
    try:
        # [FIX] Use state.memory directly (Modern Path)
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory system not available"}
            
        result = await state.memory.store_fact(content, category, confidence)
        return {"ok": True, "result": result}
    except Exception as e:
        logger.error(f"Error in tool_memory_store_fact: {e}")
        return {"ok": False, "error": str(e)}

async def tool_memory_query_facts(state: AgentState, query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search for facts in long-term memory using semantic search.
    """
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory system not available"}
            
        result = await state.memory.query_facts(query, limit)
        return {"ok": True, "result": result}
    except Exception as e:
        logger.error(f"Error in tool_memory_query_facts: {e}")
        return {"ok": False, "error": str(e)}

async def tool_memory_search_semantic(state: AgentState, query: str, limit: int = 10, threshold: float = 0.7) -> Dict[str, Any]:
    """
    Advanced semantic search over memory episodes and facts.
    """
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory system not available"}
            
        # Note: mapped to semantic_search in MemoryServer
        result = await state.memory.semantic_search(query, limit)
        return {"ok": True, "result": result}
    except Exception as e:
        logger.error(f"Error in tool_memory_search_semantic: {e}")
        return {"ok": False, "error": str(e)}
        
async def tool_memory_consolidate(state: AgentState) -> Dict[str, Any]:
    """
    Trigger a memory consolidation pass (cleanup, summarization).
    """
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory system not available"}
            
        await state.memory.consolidate()
        return {"ok": True, "result": "Consolidation triggered"}
    except Exception as e:
        logger.error(f"Error in tool_memory_consolidate: {e}")
        return {"ok": False, "error": str(e)}
