
import asyncio
import os
import sys
from pathlib import Path

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

async def purge_config():
    print("🧹 Purging Stale Sovereign Configuration...")
    state = AgentState()
    # Initialize basic state to get DB connection (but ignore loaded config)
    try:
        await state.initialize()
    except Exception:
        pass # Ignore errors, we just want the connection
        
    # FORCE DELETE
        await run_query(state, "DELETE FROM config_state;")
        print("✅ Database Configuration Purged.")
    except Exception as e:
        print(f"❌ Error purging DB: {e}")

if __name__ == "__main__":
    asyncio.run(purge_config())
