
import asyncio
import sys
import os

# Adjust path to find modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.state import AgentState
from agent_runner.tools.system import tool_add_lexicon_entry

async def test_immunization():
    print("Testing Immunization Tool...")
    # Mock State
    state = AgentState()
    
    # Test Pattern
    res = await tool_add_lexicon_entry(
        state, 
        pattern="TestError.*ConnectionRefused", 
        label="TEST_IMMUNIZATION_VERIFY", 
        severity="INFO"
    )
    
    print(f"Result: {res}")
    
    # Verify File
    import yaml
    p = state.agent_fs_root / "config" / "lexicons" / "learned_patterns.yaml"
    if p.exists():
        print(f"File exists at {p}")
        with open(p, "r") as f:
            print(f.read())
    else:
        print("File NOT created!")

if __name__ == "__main__":
    asyncio.run(test_immunization())
