import asyncio
import os
import logging
from agent_runner.agent_runner import get_shared_state
from agent_runner.config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    print("DEBUG: Getting Shared State...")
    state = get_shared_state()
    # Mock init if needed (usually main.py does it)
    # But ConfigManager needs connected MemoryServer
    print("DEBUG: Initializing Memory...")
    try:
        from agent_runner.memory_server import MemoryServer
        state.memory = MemoryServer(state)
        await state.memory.initialize()
        print("DEBUG: Memory Initialized.")
    except Exception as e:
        print(f"DEBUG: Memory Init Failed: {e}")
        return

    print("DEBUG: Initializing ConfigManager...")
    manager = ConfigManager(state)
    state.config_manager = manager
    
    # Init fs_root for path resolution
    from pathlib import Path
    state.agent_fs_root = Path(os.getcwd()) / "agent_data" # Mock
    
    print("DEBUG: Calling set_config_value...")
    try:
        success = await manager.set_config_value("VISION_MODEL", "ollama:llama3.2-vision")
        print(f"DEBUG: success={success}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
