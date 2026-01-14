
import asyncio
import os
import sys
from pathlib import Path

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from agent_runner.state import AgentState

async def introspect():
    print("🔍 Introspecting Live AgentState...")
    state = AgentState()
    # We must run initialize to load from DB/Env
    await state.initialize()
    
    roles = {
        "🧠 Maître d' (Intent)": state.intent_model,
        "🤖 Main Agent (MCP)": state.mcp_model,
        "👨‍💻 Coder (Agent)": state.agent_model,
        "🚑 Healer": state.healer_model,
        "🚦 Router": state.router_model,
        "📋 Task Manager": state.task_model,
        "📝 Summarizer": state.summarization_model,
        "🛡️ Fallback": state.fallback_model,
        "🏁 Finalizer": state.finalizer_model,
        "⚖️ Critic": state.critic_model,
        "✂️ Pruner": state.pruner_model,
        "🔎 Query Refiner": state.query_refinement_model,
        "👀 Vision": state.vision_model,
        "🔤 Embeddings": state.embedding_model
    }
    
    print("\n--- 🟢 LIVE MODEL ASSIGNMENTS ---")
    for role, model in roles.items():
        print(f"{role}: {model}")

if __name__ == "__main__":
    asyncio.run(introspect())
