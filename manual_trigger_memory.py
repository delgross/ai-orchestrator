
import asyncio
import logging
from agent_runner.agent_runner import get_shared_state
from agent_runner.memory_tasks import memory_backup_task, memory_consolidation_task

# Mock State
class MockState:
    def __init__(self):
        self.config = {}
        self.running = True

async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Triggering Memory Tasks Manually...")
    
    state = get_shared_state() # This creates a fresh state instance
    
    # 1. Backup
    print("\n[1/2] Running Memory Backup...")
    try:
        await memory_backup_task(state)
        print("✅ Backup Task Completed (or initiated).")
    except Exception as e:
        print(f"❌ Backup Task Failed: {e}")

    # 2. Consolidation
    print("\n[2/2] Running Memory Consolidation...")
    try:
        await memory_consolidation_task(state)
        print("✅ Consolidation Task Completed (or initiated).")
    except Exception as e:
        print(f"❌ Consolidation Task Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
