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
_shared_state: Optional[AgentState] = None
_shared_engine: Optional[AgentEngine] = None

def get_shared_state() -> AgentState:
    global _shared_state
    if _shared_state is None:
        _shared_state = AgentState()
    return _shared_state

def get_shared_engine() -> AgentEngine:
    global _shared_engine
    if _shared_engine is None:
        _shared_engine = AgentEngine(get_shared_state())
    return _shared_engine

async def _agent_loop(messages: List[Dict[str, Any]], model: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Compatibility wrapper for engine.agent_loop."""
    engine = get_shared_engine()
    return await engine.agent_loop(messages, model=model, tools=tools)

# Tool grouping for legacy tasks
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "mcp_proxy",
            "description": "Call a tool on an MCP server.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server": {"type": "string"},
                    "tool": {"type": "string"},
                    "arguments": {"type": "object"}
                },
                "required": ["server", "tool", "arguments"]
            }
        }
    }
]

FILE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_text",
            "description": "Read the text content of a file.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_text",
            "description": "Write text content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "overwrite": {"type": "boolean", "default": False}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List contents of a directory.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_dir",
            "description": "Create a new directory.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    }
]
