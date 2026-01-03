
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from agent_runner.memory_server import MemoryServer

async def main():
    class MockState:
        def __init__(self):
            self.embedding_model = "ollama:mxbai-embed-large:latest"
            
    print("Connecting to SurrealDB...")
    mem = MemoryServer(MockState())
    await mem.ensure_connected()
    
    tasks_to_delete = ["rag_ingest", "night_shift_refactor", "cloud_refactor_audit"]
    
    for task_name in tasks_to_delete:
        print(f"Deleting task record: {task_name}...")
        # Use DELETE statement
        res = await mem._execute_query(f"DELETE FROM task_def WHERE name = '{task_name}'")
        print(f"Result: {res}")
        
    print("Database purge complete.")

if __name__ == "__main__":
    asyncio.run(main())
