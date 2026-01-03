import asyncio
import yaml
import logging
import os
from pathlib import Path
# Add project root to sys path to import agent modules
import sys
sys.path.append(os.getcwd())

from agent_runner.state import AgentState

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("audit_drift")

async def main():
    print("=== Configuration Drift Audit ===")
    
    # 1. Initialize State (connects to DB)
    state = AgentState()
    # We call initialize to ensure DB connection, but we mock the config loading part 
    # or just use the raw memory client directly if possible.
    # state.initialize calls _load_runtime_config_from_db which is fine, 
    # but we want to inspect the DB specifically.
    
    # Manually init memory to avoid triggering the very logic we are auditing
    from agent_runner.memory_server import MemoryServer
    state.memory = MemoryServer(state)
    try:
        await state.memory.initialize()
    except Exception as e:
        print(f"CRITICAL: Could not connect to Database: {e}")
        return

    # 2. Fetch DB State
    print("\n--- [Sovereign Memory] Checking 'mcp_server' table ---")
    db_servers = []
    try:
        db_servers = await state.memory._execute_query("SELECT * FROM mcp_server")
        if not db_servers:
            print("(!) Table 'mcp_server' is EMPTY.")
        else:
            print(f"Found {len(db_servers)} servers in DB:")
            for s in db_servers:
                status = "ENABLED" if s.get('enabled', True) else "DISABLED"
                print(f"  - {s.get('name')} ({status})")
    except Exception as e:
        print(f"Error querying DB: {e}")

    # 3. Fetch Disk State (mcp.yaml)
    print("\n--- [Disk Storage] Checking 'config/mcp.yaml' ---")
    disk_servers = {}
    config_path = Path("config/mcp.yaml")
    if config_path.exists():
        with open(config_path, "r") as f:
            data = yaml.safe_load(f) or {}
            disk_servers = data.get("mcp_servers", {})
            print(f"Found {len(disk_servers)} servers in mcp.yaml:")
            for name, cfg in disk_servers.items():
                status = "ENABLED" if cfg.get('enabled', True) else "DISABLED"
                print(f"  - {name} ({status})")
    else:
        print("(!) config/mcp.yaml does NOT exist.")

    # 4. Compare (Drift Analysis)
    print("\n--- [Drift Analysis] ---")
    
    db_names = {s['name'] for s in db_servers}
    disk_names = set(disk_servers.keys())

    # In DB but not on Disk
    in_db_only = db_names - disk_names
    if in_db_only:
        print(f"[DRIFT] Present in DB, Missing from Disk: {in_db_only}")
        print("  -> RISK: If we wiped DB to reload from disk, these would be LOST.")
    
    # On Disk but not in DB
    in_disk_only = disk_names - db_names
    if in_disk_only:
        print(f"[DRIFT] Present on Disk, Missing from DB: {in_disk_only}")
        print("  -> SAFETY: DB-First boot would MISS these unless we have fallback logic.")

    # Modified? (Rough check)
    common = db_names.intersection(disk_names)
    for name in common:
        # Check enabled state match
        db_s = next(s for s in db_servers if s['name'] == name)
        disk_s = disk_servers[name]
        
        db_en = db_s.get('enabled', True)
        disk_en = disk_s.get('enabled', True)
        
        if db_en != disk_en:
            print(f"[DRIFT] State Mismatch for '{name}': DB={db_en}, Disk={disk_en}")
            print(f"  -> CONFLICT: DB says {db_en}, Disk says {disk_en}")

    if not in_db_only and not in_disk_only and len(common) > 0:
        print("✅ Sync Status: PERFECT MATCH (Set names align)")
    elif len(common) == 0 and len(db_servers) == 0:
         print("⚠️  Empty State: Database is empty.")

    print("\nAudit Complete.")

if __name__ == "__main__":
    asyncio.run(main())
