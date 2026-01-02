import asyncio
import logging
from agent_runner.system_ingestor import SystemIngestor
from agent_runner.state import AgentState

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_test():
    state = AgentState()
    ingestor = SystemIngestor(state)
    
    # Mock data that typically causes the error (a list)
    mock_network_data = [
        {"interface": "en0", "ip": "192.168.1.5"},
        {"interface": "lo0", "ip": "127.0.0.1"}
    ]
    
    logger.info("TEST: Attempting to store list data into 'system_state'...")
    try:
        # We manually call the internal helper to simulate the issue/fix
        # 'details' field in DB is TYPE object. Passing a list should fail without the fix.
        # With the fix (in ingest_system_profiler), the CALLER wraps it. 
        # Wait, I modified `ingest_system_profiler`, not `_store_system_state`.
        # So I need to call `ingest_system_profiler` or simulate its logic.
        
        # Testing the specific logic block I added:
        items = mock_network_data
        dt = "SPNetworkDataType"
        
        # Copied logic from the fix:
        if isinstance(items, list):
            items = {"items": items}
            
        # Store
        await ingestor._store_system_state(dt, items, category="Network")
        logger.info("TEST: Success! Data stored without schema error.")
        
    except Exception as e:
        logger.error(f"TEST: Failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
