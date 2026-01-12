import asyncio
import os
from agent_runner.state import AgentState

async def verify_switchover():
    print("--- Verifying Sovereign Switchover Logic ---")
    
    state = AgentState()
    
    # Setup: Prefer Cloud
    state._agent_model = "openai:gpt-4o"
    state._vision_model = "openai:gpt-4o"
    state.fallback_model = "ollama:mistral:latest" # Safe local
    
    # Case 1: Online
    state.internet_available = True
    print(f"[Online] Agent Model: {state.agent_model} (Expected: openai:gpt-4o)")
    assert state.agent_model == "openai:gpt-4o"
    
    print(f"[Online] Vision Model: {state.vision_model} (Expected: openai:gpt-4o)")
    assert state.vision_model == "openai:gpt-4o"

    # Case 2: Offline
    state.internet_available = False
    print(f"[Offline] Agent Model: {state.agent_model} (Expected: local fallback)")
    assert state.is_local_model(state.agent_model)
    assert state.agent_model == "ollama:mistral:latest"
    
    print(f"[Offline] Vision Model: {state.vision_model} (Expected: local vision fallback)")
    assert state.is_local_model(state.vision_model)
    # The property has a specific override for vision
    print(f"Vision Fallback: {state.vision_model}")
    assert "vision" in state.vision_model
    
    # Case 3: Offline but Preferred IS Local
    state._agent_model = "ollama:llama3.3"
    print(f"[Offline+LocalPref] Agent Model: {state.agent_model} (Expected: ollama:llama3.3)")
    assert state.agent_model == "ollama:llama3.3"

    print("\n✅ Verification SUCCESS: Sovereign Switchover is robust.")

if __name__ == "__main__":
    asyncio.run(verify_switchover())
