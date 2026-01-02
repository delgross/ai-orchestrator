import asyncio
import os
import sys

# Ensure we can import from ai/
sys.path.append(os.path.abspath("ai"))

from agent_runner.state import AgentState

async def verify_reverse_sync():
    print("--- Verifying Reverse Sync (Phase 46) ---")
    
    # 1. Initialize State
    # Force FS_ROOT to align with reality for this test
    os.environ["FS_ROOT"] = os.path.abspath("ai")
    state = AgentState()
    await state.initialize() 

    # 2. Set a Test Secret
    key = "TEST_REVERSE_SYNC"
    val = "sovereign_123"
    print(f"\nSetting {key}={val} via ConfigManager...")
    
    success = await state.config_manager.set_secret(key, val)
    if not success:
        print("❌ ConfigManager failed.")
        return

    # 3. Verify Runtime
    print(f"\n[Check 1] Runtime (os.environ): {'✅' if os.environ.get(key) == val else '❌'}")
    
    # 4. Verify DB
    print("\n[Check 2] Database (config_state):")
    # Use SELECT * to avoid 'value' keyword collision issues if any
    res = await state.memory._execute_query(f"SELECT * FROM config_state WHERE key = '{key}'")
    db_val = res[0]['value'] if res else None
    print(f"   found: {db_val} -> {'✅' if db_val == val else '❌'}")
    
    # 5. Verify Disk (.env)
    print("\n[Check 3] Disk (.env):")
    env_path = state.agent_fs_root / ".env"
    found_disk = False
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if line.strip().startswith(f"{key}="):
                    if val in line:
                        found_disk = True
                    break
    print(f"   found in file: {'✅' if found_disk else '❌'}")

    # Cleanup
    # await state.config_manager.set_secret(key, "DELETED") # keeping it simple for now

if __name__ == "__main__":
    asyncio.run(verify_reverse_sync())
