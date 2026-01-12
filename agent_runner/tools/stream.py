
import os
import time
from typing import Dict, Any
from agent_runner.state import AgentState

async def tool_inject_stream_message(state: AgentState, message: str, emoji: str = "💬") -> Dict[str, Any]:
    """
    Inject a message directly into the live stream (chat window).
    
    Args:
        message: The text content.
        emoji: Optional emoji prefix.
    """
    try:
        stream_path = os.path.join(os.getcwd(), "logs", "live_stream.md")
        os.makedirs(os.path.dirname(stream_path), exist_ok=True)
        
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"{timestamp} {emoji} {message}\n"
        
        with open(stream_path, "a", encoding="utf-8") as f:
            f.write(formatted)
            
        return {"ok": True, "formatted": formatted}
    except Exception as e:
        return {"ok": False, "error": str(e)}
