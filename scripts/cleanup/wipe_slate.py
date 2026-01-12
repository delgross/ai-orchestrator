"""
Complete Database, Memory, and RAG Reset Script
Wipes all data for a fresh start before implementing efficiency improvements.
"""

import asyncio
import logging
import sys
import os
import httpx

# Add path
sys.path.append(os.getcwd())

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wipe_slate")

async def wipe_memory_tables(memory: MemoryServer):
    """Wipe all memory-related tables."""
    print("\n=== Wiping Memory Tables ===")
    
    tables = [
        "episode",      # Chat history
        "fact",         # Learned facts
        "task_def",     # Task definitions (will be re-ingested from disk)
        "mcp_server",   # MCP server configs (will be re-ingested from disk)
        "config",       # System config (will be re-ingested from disk)
        "system_state", # System profiler data
        "diagnostic_log", # Log entries
        "router_analysis_cache", # Router cache (if exists)
        "sentinel_rules", # Sentinel rules (if exists)
        "ingestion_history", # Ingestion history (will be recreated in DB)
    ]
    
    for table in tables:
        try:
            await memory._execute_query(f"DELETE {table};")
            print(f"   ✅ Wiped {table}")
        except Exception as e:
            print(f"   ⚠️  {table}: {e} (may not exist)")

async def wipe_rag_data():
    """Wipe all RAG chunks and graph data."""
    print("\n=== Wiping RAG Data ===")
    
    # RAG server uses same SurrealDB
    surreal_url = os.getenv("SURREAL_URL", "http://localhost:8000")
    surreal_user = os.getenv("SURREAL_USER", "root")
    surreal_pass = os.getenv("SURREAL_PASS", "root")
    surreal_ns = os.getenv("SURREAL_NS", "orchestrator")
    surreal_db = os.getenv("SURREAL_DB", "memory")
    
    sql_url = f"{surreal_url}/sql"
    auth = (surreal_user, surreal_pass)
    headers = {
        "Accept": "application/json",
        "NS": surreal_ns,
        "DB": surreal_db,
    }
    
    rag_tables = [
        "chunk",    # RAG chunks
        "entity",   # Graph entities
        "relates",  # Graph relations
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for table in rag_tables:
            try:
                query = f"USE NS {surreal_ns}; USE DB {surreal_db}; DELETE {table};"
                resp = await client.post(sql_url, content=query, auth=auth, headers=headers)
                if resp.status_code == 200:
                    print(f"   ✅ Wiped {table}")
                else:
                    print(f"   ⚠️  {table}: HTTP {resp.status_code}")
            except Exception as e:
                print(f"   ⚠️  {table}: {e}")

async def wipe_ingestion_history_file():
    """Remove ingestion history file (will be recreated in DB)."""
    print("\n=== Cleaning Up Ingestion History File ===")
    
    from pathlib import Path
    agent_fs_root = Path(os.getenv("FS_ROOT", os.path.expanduser("~/ai/agent_fs_root")))
    history_file = agent_fs_root / "system" / "ingestion_history.json"
    
    if history_file.exists():
        # Backup before deletion
        backup_file = history_file.with_suffix(".json.backup")
        try:
            import shutil
            shutil.copy(history_file, backup_file)
            print(f"   ✅ Backed up to {backup_file}")
        except Exception as e:
            print(f"   ⚠️  Backup failed: {e}")
        
        try:
            history_file.unlink()
            print(f"   ✅ Removed {history_file}")
        except Exception as e:
            print(f"   ⚠️  Removal failed: {e}")
    else:
        print(f"   ℹ️  File doesn't exist: {history_file}")

async def main():
    print("=" * 60)
    print("COMPLETE SYSTEM RESET")
    print("=" * 60)
    print("WARNING: This will wipe ALL data from:")
    print("  - Database (episodes, facts, configs, etc.)")
    print("  - RAG chunks and graph data")
    print("  - Ingestion history file")
    print("=" * 60)
    
    # Allow non-interactive mode via environment variable
    if os.getenv("AUTO_CONFIRM") != "yes":
        try:
            response = input("\nAre you absolutely sure? Type 'YES' to continue: ")
            if response != "YES":
                print("Aborted.")
                return
        except EOFError:
            # Non-interactive mode - proceed if explicitly requested
            print("\n⚠️  Non-interactive mode detected. Use AUTO_CONFIRM=yes to proceed automatically.")
            print("Aborted for safety.")
            return
    else:
        print("\n✅ AUTO_CONFIRM=yes detected. Proceeding with reset...")
    
    print("\nInitializing State and Memory Server...")
    state = AgentState()
    memory = MemoryServer(state)
    
    # Manually initialize connection
    await memory.initialize()
    
    # Wipe all data
    await wipe_memory_tables(memory)
    await wipe_rag_data()
    await wipe_ingestion_history_file()
    
    print("\n" + "=" * 60)
    print("✅ RESET COMPLETE")
    print("=" * 60)
    print("All data has been wiped. System is ready for fresh start.")
    print("You can now implement efficiency improvements with clean slate.")

if __name__ == "__main__":
    asyncio.run(main())
