
import asyncio
import logging
from agent_runner.state import AgentState
from agent_runner.memory_tasks import memory_consolidation_task

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def manual_memory_run():
    print("🧠 Initializing Agent State...")
    # This assumes we are running in the root directory where .env is accessible
    state = AgentState()
    
    # We might need to initialize the DB client if State doesn't do it automatically
    # Check state.py or db_client.py if this fails.
    # Usually state lazy loads connection.

    print("🚀 Triggering Memory Consolidation...")
    try:
        # Mocking the args if necessary, or just passing state
        result = await memory_consolidation_task(state)
        print("\n✅ Memory Consolidation Result:")
        print(result)
    except Exception as e:
        print(f"❌ Execution Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(manual_memory_run())
