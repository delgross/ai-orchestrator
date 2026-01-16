
import asyncio
import os
import sys
# Make sure we can find agent_runner
sys.path.append(os.getcwd())

from agent_runner.state import AgentState
from agent_runner.hallucination_detector import HallucinationDetector

async def main():
    print("🔍 AUDIT: Verifying System Model Assignments...")
    
    # 1. Initialize State (Single Source of Truth)
    state = AgentState()
    state._load_base_config()
    
    print(f"\n[1] AgentState Configuration (Sovereign.yaml + DB Overrides)")
    if getattr(state, 'agent_model', None):
        print(f"    - Agent Model (Brain):      {state.agent_model}")
    else:
        print(f"    - Agent Model (Brain):      [MISSING]")
        
    print(f"    - Router Model:             {getattr(state, 'router_model', 'N/A')}")
    print(f"    - Intent Model (Maître d'): {getattr(state, 'intent_model', 'N/A')}")
    print(f"    - Auditor Model:            {getattr(state, 'auditor_model', 'N/A')}")
    print(f"    - Healer Model:             {getattr(state, 'healer_model', 'N/A')}")
    print(f"    - Summarizer Model:         {getattr(state, 'summarizer_model', 'N/A')}")
    print(f"    - Vision Model:             {getattr(state, 'vision_model', 'N/A')}")
    print(f"    - Query Refinement Model:   {getattr(state, 'query_refinement_model', 'N/A')}")
    
    # 2. Verify Hallucination Detector (Auditor)
    print(f"\n[2] Component: HallucinationDetector (Auditor)")
    try:
        hd = HallucinationDetector(state)
        # Check specific analyzer if available
        model = hd.llm_analyzer.model_name
        print(f"    - REAL RUNTIME MODEL:       {model}")
        if "ollama:" in model:
             print(f"    ❌ WARNING: Prefix 'ollama:' detected! API calls will fail.")
        else:
             print(f"    ✅ Prefix stripped correctly.")
    except Exception as e:
        print(f"    ❌ Initialization Failed: {e}")

    # 3. Intent Engine is Functional
    print(f"\n[3] Component: IntentEngine (Maître d')")
    print(f"    - Functional Component. Uses state.intent_model: {getattr(state, 'intent_model', 'N/A')}")
    if getattr(state, 'intent_model', '').startswith('ollama:'):
        print("    ℹ️  Note: Maître d' logic handles prefix stripping internally in intent.py")

    print("\n✅ Audit Complete.")

if __name__ == "__main__":
    asyncio.run(main())
