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
    
    print("\n--- Removing Weather MCP (Direct DB) ---")
    query = "DELETE FROM mcp_server WHERE name = 'weather'"
    res = await state.memory._execute_query(query)
    print(f"DB Result: {res}")
    print("✅ Ensure Weather MCP is removed.")
        
    await state.close_http_client()

if __name__ == "__main__":
    asyncio.run(main())
