import asyncio
import json
from agent_runner.state import AgentState
from agent_runner.tools.mcp import tool_mcp_proxy

async def check():
    state = AgentState()
    # Mock config for tool call
    state.mcp_servers = {"project-memory": {"type": "stdio", "cmd": ["/Users/bee/Sync/Antigravity/ai/agent_runner/.venv/bin/python", "/Users/bee/Sync/Antigravity/ai/agent_runner/memory_server.py"], "env": {"SURREAL_URL": "ws://127.0.0.1:8000/rpc"}}}
    
    with open("memory_check_result.txt", "w") as f:
        f.write("Starting check...\n")
        try:
            res = await tool_mcp_proxy(state, "project-memory", "semantic_search", {"query": "verification", "limit": 5}, bypass_circuit_breaker=True)
            f.write(json.dumps(res, indent=2))
        except Exception as e:
            f.write(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
