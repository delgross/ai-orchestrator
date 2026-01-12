
import asyncio
import contextvars
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_runner.state import AgentState
from agent_runner.quality_tiers import QualityTier, get_tier_config

async def test_context_vars():
    print("Testing ContextVars isolation...")
    state = AgentState()
    
    # helper to run in a context
    async def task_a():
        state._request_quality_tier = QualityTier.FASTEST
        await asyncio.sleep(0.1)
        assert state._request_quality_tier == QualityTier.FASTEST
        print("Task A: ContextVar persisted correctly")
        
    async def task_b():
        state._request_quality_tier = QualityTier.MAXIMUM
        await asyncio.sleep(0.1)
        assert state._request_quality_tier == QualityTier.MAXIMUM
        print("Task B: ContextVar persisted correctly")

    await asyncio.gather(task_a(), task_b())
    
    # Main context should use default (None -> BALANCED)
    assert state.get_quality_tier_for_request() == QualityTier.BALANCED
    print("Main Context: Defaulted to globally configured tier (BALANCED)")
    print("✅ ContextVars test passed")

async def test_async_tempo():
    print("\nTesting Async Tempo...")
    state = AgentState()
    
    # Mock active requests to force system check
    state.active_requests = 0
    
    # We can't easily mock subprocess here without extensive patching, 
    # but we can call it and ensure it doesn't crash and returns a Tempo enum.
    # Note: On CI/CD environment ioreg might fail, but it should fallback gracefully.
    
    start = asyncio.get_event_loop().time()
    tempo = await state.get_current_tempo()
    end = asyncio.get_event_loop().time()
    
    print(f"Tempo returned: {tempo}")
    print(f"Execution time: {end - start:.4f}s")
    
    assert hasattr(tempo, "name")
    print("✅ Async Tempo test passed")

async def main():
    try:
        await test_context_vars()
        await test_async_tempo()
        print("\n🎉 ALL CHECKS PASSED")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
