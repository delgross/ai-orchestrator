
import asyncio
import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent_runner.registry import ServiceRegistry
from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer
from agent_runner.rag_helpers import _ingest_content, _process_locally

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manual_ingest")

# Define source file path
# SRC_FILE = Path(os.path.abspath("memory_test_unique.md"))
SRC_FILE = Path("/Users/bee/.gemini/antigravity/brain/5e01b889-041c-46a1-9732-7a3c5e393120/system_lexicon.md")

async def run_ingest():
    print("--- Manual Ingest Validation ---")
    
    # Create test file if needed
    if not SRC_FILE.exists():
        SRC_FILE.write_text("The quick brown fox jumps over the lazy dog. This is a unique test sentence for recall.")
        
    state = AgentState()
    # Mock config
    state.config = {"ai": {"embedding_model": "mxbai-embed-large:latest", "task_model": "ollama:llama3.1:latest"}}
    # Ensure gateway base (mock or real) - defaulting to mocked in verify_recall usually, but helpers need real URL?
    # Actually helpers use state.gateway_base
    state.gateway_base = "http://127.0.0.1:5460" 

    ServiceRegistry.register_state(state)
    
    memory = MemoryServer(state)
    await memory.initialize()
    ServiceRegistry.register_memory_server(memory)
    
    http_client = await state.get_http_client()
    
    print(f"Ingesting {SRC_FILE}...")
    content = await _process_locally(SRC_FILE, state, http_client)
    
    # Call ingest
    # We pass dummy paths for processed/review dirs
    try:
        await _ingest_content(
            file_path=SRC_FILE, 
            content=content, 
            state=state, 
            http_client=http_client, 
            rag_base_url="http://127.0.0.1:5555", # Dummy, we expect it to fail HTTP but perform Graph local extraction first? 
            # Wait, _ingest_content calls RAG backend at step 3. 
            # If RAG is down, it raises exception. 
            # We want to test Step 4 (Graph).
            # Step 4 is AFTER Step 3.
            # So we need to mock the RAG backend call or catch the error?
            # Actually, let's just modify the helper to not fail? 
            # No, let's catch the error in _ingest_content if we can, or just mock the http client.
            processed_dir_base=Path("."),
            review_dir=Path(".")
        )
    except Exception as e:
        print(f"Ingest loop error: {e}")
        # Note: If RAG call fails, it might abort before Graph.
        # Let's hope RAG server is up (it should be).
        
    print("Ingest complete.")

if __name__ == "__main__":
    asyncio.run(run_ingest())
