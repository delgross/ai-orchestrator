#!/usr/bin/env python3
"""
Delete corrupted episode records that have NULL required fields.
These records are incomplete and cause schema validation errors.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

async def delete_corrupted_episodes():
    """Delete episode records with NULL required fields."""
    print("🗑️  Deleting corrupted episode records...\n")
    
    state = AgentState()
    state.memory = MemoryServer(state)
    await state.memory.initialize()
    
    # Find records with NULL values
    query = "SELECT id, request_id FROM episode WHERE kb_id IS NONE OR session_id IS NONE OR role IS NONE OR content IS NONE"
    corrupted = await state.memory._execute_query(query)
    
    if not corrupted or len(corrupted) == 0:
        print("✅ No corrupted records found.")
        return
    
    print(f"Found {len(corrupted)} corrupted record(s):")
    for r in corrupted:
        print(f"  - {r.get('id')}: request_id={r.get('request_id')}")
    
    # Confirm
    print(f"\n⚠️  About to delete {len(corrupted)} record(s)")
    print("These records are corrupted and cannot be used.")
    
    # Delete each record
    print("\nDeleting records...")
    deleted = 0
    for r in corrupted:
        record_id = r.get('id')
        request_id = r.get('request_id')
        
        try:
            # Extract ID part for type::thing()
            if ':' in record_id:
                id_part = record_id.split(':', 1)[1]
            else:
                id_part = record_id
            
            # Delete the record
            delete_query = "DELETE type::thing('episode', $id)"
            result = await state.memory._execute_query(
                delete_query,
                {"id": id_part}
            )
            
            if result is not None:
                print(f"  ✅ Deleted: {record_id}")
                deleted += 1
            else:
                print(f"  ⚠️  No result for: {record_id}")
        except Exception as e:
            print(f"  ❌ Failed to delete {record_id}: {e}")
    
    print(f"\n✅ Deletion complete: {deleted}/{len(corrupted)} records deleted")
    
    # Verify
    remaining = await state.memory._execute_query(
        "SELECT count() FROM episode WHERE kb_id IS NONE OR session_id IS NONE OR role IS NONE OR content IS NONE GROUP ALL"
    )
    if remaining and remaining[0].get('count', 0) > 0:
        print(f"⚠️  Warning: {remaining[0].get('count')} corrupted records still remain")
    else:
        print("✅ All corrupted records removed")

if __name__ == "__main__":
    try:
        asyncio.run(delete_corrupted_episodes())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


