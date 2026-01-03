import asyncio
import os
import sys
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from agent_runner.state import AgentState

async def main():
    print("Initializing Agent State...")
    state = AgentState()
    await state.initialize()
    
    print("\n--- Current MCP Servers ---")
    for name, cfg in state.mcp_servers.items():
        print(f"- {name}: {cfg.get('enabled')} ({cfg.get('type')})")
        
    print("\n--- Injecting Weather MCP ---")
    weather_config = {
        "command": "uvx",
        "args": ["mcp-server-weather"],
        "env": {},
        "enabled": True,
        "type": "stdio"
    }
    
    await state.add_mcp_server("weather", weather_config)
    print("✅ Weather MCP added to Sovereign Memory.")
    
    # Check Tavily
    tavily = state.mcp_servers.get("tavily-search")
    if tavily:
        print(f"\nTavily Config: {tavily}")
    else:
        print("\n⚠️ Tavily NOT found.")

    await state.close_http_client()

if __name__ == "__main__":
    asyncio.run(main())
