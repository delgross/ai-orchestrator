
import asyncio
import sys
import os
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
    print("Testing investigate_system_performance()...")
    state = MockState()
    
    # Run in background=False mode (if supported) or just let it fire async and wait a bit
    # The tool returns immediately if background=True.
    # But our implementation of _run_investigation_background is async.
    # The tool uses asyncio.create_task.
    
    # We will invoke the internal background worker directly to see output, 
    # or just call the tool and sleep.
    
    res = await tool_investigate_system_performance(state, components=["latency", "zombies"], background=True)
    print(f"Tool Result: {res}")
    
    # Wait for background task to likely finish (it writes to file)
    print("Waiting 3s for background task...")
    await asyncio.sleep(3)
    print("Done.")

if __name__ == "__main__":
    asyncio.run(run_test())
