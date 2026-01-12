import asyncio
import logging
from agent_runner.tools.web import tool_search_web
from agent_runner.state import AgentState

# Setup Mock State
class MockState(AgentState):
    def __init__(self):
        pass

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Verifying tool_search_web...")
    state = MockState()
    
    # Test 1: Simple Query
    res = await tool_search_web(state, "Starlink launch schedule")
    print(f"Result OK: {res.get('ok')}")
    if res.get("ok"):
        content = res.get("result", "")
        print(f"Content Length: {len(content)}")
        print(f"Preview: {content[:200]}...")
        if "Starlink" in content:
             print("SUCCESS: Found relevant content.")
        else:
             print("WARNING: Content might not be relevant.")
    else:
        print(f"FAILURE: {res.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
