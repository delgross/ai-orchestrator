
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agent_runner.memory_server import MemoryServer

async def main():
    mem = MemoryServer()
    await mem.ensure_connected()
    
    print("Populating 'system_architecture' bank...")
    res = await mem.index_own_architecture()
    print(res)
    
    print("\nListing Banks:")
    banks = await mem.list_memory_banks()
    print(banks)

if __name__ == "__main__":
    asyncio.run(main())
