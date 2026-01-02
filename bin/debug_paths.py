import asyncio
import os
import sys

# Ensure we can import from ai/
sys.path.append(os.path.abspath("ai"))

from agent_runner.state import AgentState

def check_paths():
    print("--- Debugging Paths ---")
    state = AgentState()
    print(f"CWD: {os.getcwd()}")
    print(f"State FS Root: {state.agent_fs_root}")
    
    env_path = os.path.join(state.agent_fs_root or os.getcwd(), ".env")
    print(f"Calculated .env path: {env_path}")
    print(f"Exists: {os.path.exists(env_path)}")

if __name__ == "__main__":
    check_paths()
