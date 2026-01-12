
import asyncio
import os
import sys
import logging
import yaml
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("restore_db")

async def main():
    logger.info("🚀 Starting Sovereign Memory Restoration...")
    
    # 1. Initialize State & Memory
    state = AgentState()
    memory = MemoryServer(state)
    try:
        await memory.initialize()
        logger.info("✅ Connected to SurrealDB")
    except Exception as e:
        logger.error(f"❌ Failed to connect to DB: {e}")
        return

    # 2. Read mcp.yaml (The Backup)
    yaml_path = Path(__file__).parent.parent / "config" / "mcp.yaml"
    if not yaml_path.exists():
        logger.error(f"❌ mcp.yaml not found at {yaml_path}")
        return
        
    try:
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f) or {}
            servers = data.get("mcp_servers", {})
            logger.info(f"📄 Found {len(servers)} servers in mcp.yaml")
    except Exception as e:
        logger.error(f"❌ Failed to parse mcp.yaml: {e}")
        return

    # 3. Restore to Database (The Truth)
    count = 0
    for name, config in servers.items():
        # Normalize cmd
        cmd = config.get("command") or config.get("cmd", [])
        if isinstance(cmd, list) and len(cmd) > 0:
             command = cmd[0]
             args = cmd[1:]
        elif isinstance(cmd, str):
             command = cmd
             args = config.get("args", [])
        else:
             command = ""
             args = []

        record = {
            "name": name,
            "command": command,
            "args": args,
            "env": config.get("env", {}),
            "enabled": config.get("enabled", True),
            "type": config.get("type", "stdio")
        }
        
        # UPSERT
        try:
            q = "UPSERT mcp_server CONTENT $data"
            # Delete first to ensure clean state for this record? Or just upsert?
            # UPSERT is safer for partial updates, but we want to Enforce Config.
            # Let's use the exact logic from config_manager
            await memory._execute_query(f"DELETE FROM mcp_server WHERE name = '{name}'; {q}", {"data": record})
            logger.info(f"   - Restored: {name}")
            count += 1
        except Exception as e:
            logger.error(f"   - Failed {name}: {e}")

    logger.info(f"✅ Restoration Complete. {count} servers restored to Sovereign Memory.")
    logger.info("The Database is now the Pristine Source of Truth.")

if __name__ == "__main__":
    asyncio.run(main())
