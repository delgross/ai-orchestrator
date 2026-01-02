
import asyncio
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agent_runner.memory_server import MemoryServer

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

async def main():
    print("=== Verifying Memory Banks ===")
    print("Instantiating MemoryServer...")
    from unittest.mock import MagicMock
    mock_state = MagicMock()
    mock_state.internet_available = True
    mem = MemoryServer(state=mock_state)
    await mem.ensure_connected()
    
    # 1. Setup: Create facts in two banks
    print("1. Creating Test Banks...")
    await mem.store_fact("Project", "is_in", "Alpha", context={"kb_id": "test_bank_alpha"})
    await mem.store_fact("Project", "is_in", "Beta", context={"kb_id": "test_bank_beta"})
    
    # 2. List Banks
    print("2. Listing Banks...")
    res = await mem.list_memory_banks()
    banks = res.get("banks", [])
    bank_ids = [b["kb_id"] for b in banks]
    print(f"   Found banks: {bank_ids}")
    
    if "test_bank_alpha" in bank_ids and "test_bank_beta" in bank_ids:
        print(f"   {GREEN}PASS: Both banks created.{RESET}")
    else:
        print(f"   {RED}FAIL: Banks missing.{RESET}")
        return

    # 3. Test Isolation (Filtering)
    print("3. Testing Isolation...")
    q_res = await mem.query_facts(kb_id="test_bank_alpha", limit=10)
    facts = q_res.get("facts", [])
    targets = [f["target"] for f in facts]
    
    if "Alpha" in targets and "Beta" not in targets:
        print(f"   {GREEN}PASS: Filtered correctly (Saw Alpha, Hid Beta).{RESET}")
    else:
        print(f"   {RED}FAIL: Filter failed (Targets: {targets}).{RESET}")

    # 4. Test Deletion
    print("4. Testing Deletion...")
    await mem.delete_memory_bank("test_bank_alpha")
    
    res_after = await mem.list_memory_banks()
    bank_ids_after = [b["kb_id"] for b in res_after.get("banks", [])]
    
    if "test_bank_alpha" not in bank_ids_after and "test_bank_beta" in bank_ids_after:
        print(f"   {GREEN}PASS: Alpha deleted, Beta remains.{RESET}")
    else:
        print(f"   {RED}FAIL: Deletion failed (Banks: {bank_ids_after}).{RESET}")

    # Cleanup Beta
    await mem.delete_memory_bank("test_bank_beta")
    print(f"\n{GREEN}=== MEMORY BANK VERIFICATION COMPLETE ==={RESET}")

if __name__ == "__main__":
    asyncio.run(main())
