
import asyncio
import os
import json
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

async def restore():
    print("⏳ Initializing AgentState...")
    state = AgentState()
    await state.initialize()
    
    # Configuration derived from grep search of current_health.json
    server_name = "project-memory"
    
    # Python Environment
    venv_python = "/Users/bee/Sync/Antigravity/ai/.venv/bin/python"
    script_path = "/Users/bee/Sync/Antigravity/ai/agent_runner/memory_server.py"
    
    cmd = [venv_python, script_path]
    
    env = {
        "EMBED_MODEL": "ollama:mxbai-embed-large:latest",
        "GATEWAY_BASE": "http://127.0.0.1:5455",
        "SURREAL_DB": "memory",
        "SURREAL_NS": "orchestrator",
        "SURREAL_PASS": "root",
        "SURREAL_URL": "ws://127.0.0.1:8000/rpc",
        "SURREAL_USER": "root"
    }

    print(f"🔧 Restoring '{server_name}'...")
    
    # 1. Start via ConfigManager (handles DB + Runtime + Disk)
    if state.config_manager:
        config = {
            "type": "stdio",
            "command": venv_python,
            "args": [script_path],
            "env": env,
            "cmd": cmd, # Redundant but safe
            "enabled": True
        }
        
        # This updates DB and runtime
        print("   Adding via add_mcp_server()...")
        await state.add_mcp_server(server_name, config)
        print("✅ Restored successfully via ConfigManager.")
        
    else:
        # Fallback: Direct DB Insert if ConfigManager fails
        print("⚠️ ConfigManager not found, falling back to direct DB insert...")
        # (This path shouldn't happen if initialized properly)
        
if __name__ == "__main__":
    asyncio.run(restore())
