import asyncio
import os
import logging
from agent_runner.state import AgentState
from agent_runner.rag_ingestor import rag_ingestion_task

logging.basicConfig(level=logging.INFO)

async def main():
    print("Initializing State...")
    state = AgentState()
    # Emulate startup
    state.agent_fs_root = os.path.expanduser("~/ai")
    
    print("Triggering Ingestion Task...")
    await rag_ingestion_task(state)
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
