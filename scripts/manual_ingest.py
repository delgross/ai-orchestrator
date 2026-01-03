import asyncio
import logging
import os
from pathlib import Path
from agent_runner.rag_ingestor import rag_ingestion_task
from agent_runner.state import AgentState
from agent_runner.registry import ServiceRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manual_ingest")

async def main():
    logger.info("Starting Manual Ingestion Run (V2)...")
    state = parse_minimal_state()
    trigger = Path("/Users/bee/Sync/Antigravity/ai/agent_fs_root/ingest/.trigger_now")
    trigger.touch()
    await rag_ingestion_task(rag_base_url="http://127.0.0.1:5555", state=state)
    logger.info("Manual Ingestion Complete.")

def parse_minimal_state():
    class MockState:
        def __init__(self):
            self.internet_available = True
            self.vision_model = "gpt-4o"
            self.task_model = "gpt-4o"
            self.gateway_base = "http://127.0.0.1:8000"
            self.agent_fs_root = Path("/Users/bee/Sync/Antigravity/ai/agent_fs_root")
            self.shutdown_event = None
        async def get_http_client(self):
            import httpx
            return httpx.AsyncClient(timeout=60.0)
    return MockState()

if __name__ == "__main__":
    asyncio.run(main())
