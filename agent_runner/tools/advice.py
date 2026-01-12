import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger("agent_runner.tools.advice")

async def tool_consult_advice(state: Any, topic: str) -> Dict[str, Any]:
    """
    [Safety Net] Manually fetch advice/policy for a specific topic.
    Use this if you feel the injected advice is insufficient or missing.
    """
    try:
        path = os.path.join(state.agent_root, "config", "advice_registry.md")
        if not os.path.exists(path):
            return {"result": "Advice registry not found."}
            
        content = ""
        capturing = False
        topic = topic.strip().lower()
        
        with open(path, "r") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("- ") and not stripped.startswith("- Rule"):
                    current_topic = stripped[2:].strip().lower()
                    # Simple fuzzy match or exact match
                    if topic in current_topic or current_topic in topic:
                        capturing = True
                        content += f"\nTOPIC: {stripped[2:].strip()}\n"
                    else:
                        capturing = False
                elif capturing:
                    if stripped.startswith("- Rule") or stripped:
                        content += line
                        
        if not content:
            return {"result": f"No advice found for topic '{topic}'. Available topics can be found in config/advice_registry.md"}
            
        return {"result": content}

    except Exception as e:
        logger.error(f"Consult advice failed: {e}")
        return {"error": str(e)}

async def tool_debug_view_last_prompt(state: Any) -> Dict[str, Any]:
    """
    [Debug] View the exact System Prompt used for the last turn.
    """
    prompt = getattr(state, "last_system_prompt", "No prompt recorded yet.")
    # Return as markdown code block for readability
    return {"result": f"```text\n{prompt}\n```"}

async def tool_debug_view_active_advice(state: Any) -> Dict[str, Any]:
    """
    [Debug] View the Advice Topics that were active in the last turn.
    """
    topics = getattr(state, "last_active_advice", [])
    if not topics:
        return {"result": "No advice was active in the last turn."}
    return {"result": f"Active Advice Topics: {', '.join(topics)}"}
