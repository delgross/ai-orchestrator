
import asyncio
import os
import sys
from pathlib import Path

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from agent_runner.state import AgentState

async def force_align_db():
    print("🔧 Force Aligning Sovereign DB to Qwen 2.5...")
    state = AgentState()
    try:
        await state.initialize()
    except:
        pass
    
    # The Grid
    config_map = {
        "AGENT_MODEL": "ollama:llama3.3:70b",
        "ROUTER_MODEL": "ollama:qwen2.5:7b-instruct",
        "TASK_MODEL": "ollama:qwen2.5:7b-instruct",
        "SUMMARIZATION_MODEL": "ollama:qwen2.5:7b-instruct",
        "MCP_MODEL": "ollama:qwen2.5:7b-instruct",
        "FINALIZER_MODEL": "ollama:qwen2.5:7b-instruct",
        "CRITIC_MODEL": "ollama:qwen2.5:7b-instruct",
        "HEALER_MODEL": "ollama:qwen2.5:7b-instruct",
        "FALLBACK_MODEL": "ollama:qwen2.5:7b-instruct",
        "INTENT_MODEL": "ollama:llama3.3:70b",
        "PRUNER_MODEL": "ollama:qwen2.5:7b-instruct",
        "QUERY_REFINEMENT_MODEL": "ollama:qwen2.5:7b-instruct",
        "VISION_MODEL": "ollama:llama3.2-vision:latest",
        "EMBEDDING_MODEL": "ollama:mxbai-embed-large:latest"
    }

    if state.config_manager:
        for key, val in config_map.items():
            print(f"  - Setting {key} -> {val}")
            await state.config_manager.set_config_value(key, val)
        print("✅ DB Alignment Complete.")
    else:
        print("❌ ConfigManager not loaded.")

if __name__ == "__main__":
    asyncio.run(force_align_db())
