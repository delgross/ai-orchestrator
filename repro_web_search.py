import asyncio
import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO)

try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        HAS_DDGS = True
    except ImportError:
        HAS_DDGS = False
        DDGS = None

# Mock AgentState
class MockState:
    def __init__(self):
        self.internet_available = True

# Mock AgentState needs to be compatible with tool expectations
from agent_runner.state import AgentState

# We need to monkeypatch the tool's import or modify the tool code.
# But since we are testing if the library works, let's just test the library directly first.

async def test_library_direct():
    print("\n--- Testing DDGS Library Direct ---")
    if not DDGS:
        print("DDGS not found")
        return

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("weather 2026-01-13 Granville and Newark Ohio", max_results=5))
            print(f"Found {len(results)} results")
            for r in results:
                print(r)
    except Exception as e:
        print(f"Library Error: {e}")

# Add path so we can import agent_runner
sys.path.append(os.getcwd())

from agent_runner.tools.web import tool_search_web

async def main():
    print("--- Starting Reproduction Test ---")
    query = "weather 2026-01-13 Granville and Newark Ohio"
    state = MockState()

    print(f"Query: {query}")
    try:
        result = await tool_search_web(state, query)
        print("\n--- Result ---")
        print(result)
    except Exception as e:
        print("\n--- CRASH ---")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
