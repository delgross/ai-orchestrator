
import asyncio
import os
import sys
from pathlib import Path

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

async def dump_db():
    print("🔍 Dumping DB Config State...")
    state = AgentState()
    # Initialize enables DB connection (and loads config, but we query raw)
    try:
        await state.initialize()
    except:
        pass
        
    try:
        results = await run_query(state, "SELECT * FROM config_state;")
        print(f"📊 Rows Found: {len(results)}")
        for row in results:
            print(f" - {row.get('key')}: {row.get('value')}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(dump_db())
