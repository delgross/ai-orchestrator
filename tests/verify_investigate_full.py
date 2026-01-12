
import asyncio
import sys
from pathlib import Path

# Setup Path
sys.path.append(str(Path.cwd()))

from agent_runner.state import AgentState
from agent_runner.tools.latency import tool_investigate_system_performance

# Mock State
class MockState:
    gateway_base = "http://127.0.0.1:5455"
    agent_fs_root = Path.cwd()
    router_auth_token = None
    
    def __init__(self):
        self.config = {}

async def run_test():
    print("Testing FULL investigate_system_performance()...")
    state = MockState()
    
    # Run the remaining components
    # components=["mcp", "ingestor", "dashboard"]
    
    res = await tool_investigate_system_performance(state, components=["mcp", "ingestor", "dashboard"], background=True)
    print(f"Tool Result: {res}")
    
    # Wait for background task
    print("Waiting 3s for background task...")
    await asyncio.sleep(3)
    print("Done.")

if __name__ == "__main__":
    asyncio.run(run_test())
