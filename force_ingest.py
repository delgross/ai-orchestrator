
import asyncio
import logging
from agent_runner.state import AgentState
from agent_runner.system_ingestor import SystemIngestor

logging.basicConfig(level=logging.INFO)

async def main():
    state = AgentState()
    ingestor = SystemIngestor(state)
    await ingestor.memory.ensure_connected()
    
    print("Forcing .env ingestion...")
    await ingestor.ingest_env()
    print(".env ingestion complete.")
    
    print("Forcing Config ingestion...")
    await ingestor.ingest_config()
    print("Config ingestion complete.")

if __name__ == "__main__":
    asyncio.run(main())
