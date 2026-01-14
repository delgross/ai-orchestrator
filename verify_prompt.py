
import asyncio
import os
import sys

# Ensure module path
sys.path.append(os.getcwd())

from agent_runner.state import AgentState
from agent_runner.engine import AgentEngine

async def main():
    try:
        # Initialize minimal state
        state = AgentState()
        # Mock Location Removed to test default "Granville, OH"
        # state.location = {"city": "New York", "region": "NY", "country": "US"}
        
        engine = AgentEngine(state)
        
        # Mock _generate_search_query
        async def mock_gen_query(*args, **kwargs):
            return "test query"
        engine._generate_search_query = mock_gen_query

        # Mock tool_mcp_proxy (imported inside the method, so we can't patch the import easily)
        # But wait, python imports are cached.
        # However, it's imported INSIDE the method: `from agent_runner.tools.mcp import tool_mcp_proxy`
        # To patch that, I'd need to patch sys.modules or something.
        # Alternatively, since I controlled `engine.py`, I know it calls `await tool_mcp_proxy(...)`
        
        # ACTUALLY, simpler approach:
        # Patch `engine.memory.retrieve`?
        # Lines 350+ of engine.py seem to use `tool_mcp_proxy` for "project-memory" facts?
        # Let's re-read line 320: `arch_res = await tool_mcp_proxy(...)`
        # And later it does memory retrieval.
        
        # Let's try passing `user_messages` and see if my previous `engine.memory.retrieve` patch works.
        # I suspect `engine.memory` usage is what fills `memory_facts`?
        # Let's check `get_system_prompt` again?
        # Lines 350-370 parse `search_res`.
        # Where does `search_res` come from?
        # `search_res = await tool_mcp_proxy(...)` likely.
        
        # Okay, mocking `tool_mcp_proxy` is hard if it's a local import.
        # BUT, I can just patch `get_system_prompt` to force variables.
        # No, that defeats the purpose of verifying the code.
        
        # Let's patch `sys.modules` to inject a mock `tool_mcp_proxy`.
        from unittest.mock import MagicMock 
        mock_mcp = MagicMock()
        async def mock_proxy(*args, **kwargs):
            # return structure matching what engine expects
            return {
                "ok": True, 
                "result": {
                    "content": [{
                        "type": "text", 
                        "text": "{\"facts\": [{\"entity\": \"User\", \"relation\": \"prefers\", \"target\": \"Dark Mode\"}]}"
                    }]
                }
            }
        
        # We need to ensure when engine imports `from agent_runner.tools.mcp import tool_mcp_proxy`, it gets ours.
        # Since we strictly imported `AgentEngine` already, the module might be loaded.
        # But the function import happens at runtime.
        import sys
        import types
        mock_module = types.ModuleType("agent_runner.tools.mcp")
        mock_module.tool_mcp_proxy = mock_proxy
        sys.modules["agent_runner.tools.mcp"] = mock_module
        
        # Pass a dummy message to trigger the logic
        prompt = await engine.get_system_prompt(user_messages=[{"role": "user", "content": "hi"}])
        
        print("--- START SYSTEM PROMPT ---")
        print(prompt)
        print("--- END SYSTEM PROMPT ---")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
