#!/usr/bin/env python3
"""
Migrate existing episode records to set missing required fields.
Fixes NULL values for kb_id, session_id, and role.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

async def migrate_episodes():
    """Fix existing episode records with NULL values."""
    print("🔧 Migrating episode records to fix NULL values...")
    
    state = AgentState()
    state.memory = MemoryServer(state)
    await state.memory.initialize()
    
    # Find records with NULL values
    query = "SELECT id, request_id FROM episode WHERE kb_id IS NONE OR session_id IS NONE OR role IS NONE"
    null_records = await state.memory._execute_query(query)
    
    if not null_records or len(null_records) == 0:
        print("✅ No records with NULL values found.")
        return
    
    print(f"Found {len(null_records)} record(s) with NULL values:")
    for r in null_records:
        print(f"  - {r.get('id')}: request_id={r.get('request_id')}")
    
    # Update each record
    print("\nUpdating records...")
    updated = 0
    for r in null_records:
        record_id = r.get('id')
        request_id = r.get('request_id')
        
        try:
            # Use type::thing() to construct the record ID properly
            # Extract the ID part from record_id (e.g., "episode:ea130bd3" -> "ea130bd3")
            if ':' in record_id:
                id_part = record_id.split(':', 1)[1]
            else:
                id_part = record_id
            
            # Use UPDATE with MERGE to preserve existing fields
            update_query = """
            UPDATE type::thing('episode', $id) MERGE {
                kb_id: 'default',
                session_id: $request_id,
                role: 'user'
            }
            """
            result = await state.memory._execute_query(
                update_query,
                {"id": id_part, "request_id": request_id}
            )
            if result:
                print(f"  ✅ Updated: {record_id}")
                updated += 1
            else:
                print(f"  ⚠️  No result for: {record_id}")
        except Exception as e:
            print(f"  ❌ Failed to update {record_id}: {e}")
    
    print(f"\n✅ Migration complete: {updated}/{len(null_records)} records updated")
    
    # Verify
    remaining = await state.memory._execute_query(
        "SELECT count() FROM episode WHERE kb_id IS NONE OR session_id IS NONE OR role IS NONE GROUP ALL"
    )
    if remaining and remaining[0].get('count', 0) > 0:
        print(f"⚠️  Warning: {remaining[0].get('count')} records still have NULL values")
    else:
        print("✅ All records now have required fields set")

if __name__ == "__main__":
    try:
        asyncio.run(migrate_episodes())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

