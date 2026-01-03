
import asyncio
import os
import sys

# Add path
sys.path.append(os.getcwd())

from agent_runner.engine import AgentEngine
from agent_runner.state import AgentState

async def main():
    print("Initializing AgentState...")
    try:
        state = AgentState()
        # Mocking circuit breaker to match expected structure if it's not fully init
        if not hasattr(state, "mcp_circuit_breaker"):
             print("State has no mcp_circuit_breaker, mocking it.")
             class MockCB:
                 def get_status(self): return {}
             state.mcp_circuit_breaker = MockCB()
    except Exception as e:
        print(f"State Init Failed: {e}")
        return

    print("Initializing AgentEngine...")
    try:
        engine = AgentEngine(state)
        # Mock registry cache
        engine.registry_cache = "MOCK_REGISTRY"
    except Exception as e:
        print(f"Engine Init Failed: {e}")
        return

    print("Calling get_system_prompt...")
    try:
        prompt = await engine.get_system_prompt([], skip_refinement=True)
        print("Prompt constructed successfully.")
        print(f"Length: {len(prompt)}")
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
