#!/usr/bin/env python3
"""Check if mtime values are being cached in database"""
import asyncio
from agent_runner.db_utils import run_query
from agent_runner.state import AgentState

async def main():
    state = AgentState()
    
    # Query for all mtime keys
    query = "SELECT * FROM config_state WHERE key ~ 'mtime' ORDER BY key"
    results = await run_query(state, query)
    
    print(f"\n=== Mtime Cache Status ===")
    print(f"Found {len(results)} mtime entries:\n")
    
    for row in results:
        key = row.get('key', 'unknown')
        value = row.get('value', '')
        print(f"  {key}: {value}")
    
    if not results:
        print("  ❌ No mtime cache entries found!")
        print("  This means mtime optimization is not active.")
    else:
        print(f"\n✅ Mtime cache is populated")

if __name__ == "__main__":
    asyncio.run(main())
