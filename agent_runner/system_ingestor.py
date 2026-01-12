import os
import json
import yaml
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from agent_runner.memory_server import MemoryServer
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query_with_memory

logger = logging.getLogger("system_ingestor")

class SystemIngestor:
    def __init__(self, state: AgentState):
        self.state = state
        self.memory = MemoryServer(state)
        self.fs_root = state.agent_fs_root or os.getcwd()
        self.brain_dir = Path(os.getenv("BRAIN_DIR", "/Users/bee/Brain/Permanent_Memory")).resolve()

    async def run(self):
        """Main entry point: Ingests all system state into DB."""
        logger.info("Starting System State Ingestion...")
        try:
            await self.memory.ensure_connected()
            await self.memory.ensure_schema() # Ensure new tables exist

            # [PHASE 45] Sovereign Check: Do we need to digest disk?
            if await self.check_db_state():
                logger.info("Database Config present. Skipping File Ingestion (Sovereign Mode).")
                # Even in Sovereign Mode, we sync Task Definitions from disk as they are code-deployment artifacts
                await self.ingest_task_definitions()
                # MCP Config is also code-deployment artifact (Manifests), so we sync it
                await self.ingest_mcp_servers()
                return

            await self.ingest_env()
            await self.ingest_config()
            await self.ingest_registry() # [NEW] Sovereign YAML Ingestion
            await self.ingest_system_profiler()
            await self.ingest_task_definitions()
            # [PHASE 46] Universal Sovereign Memory Sync
            # This ensures BRAIN_DIR files are mirrored to DB (Wipe & Replace)
            await self.ingest_permanent_memory()
            # [PHASE 47] Project Registry Sync
            # This ensures data/permanent/ files are mirrored to DB (Project-specific context)
            await self.ingest_project_registry()
            
            logger.info("System State Ingestion Complete.")
            
        except Exception as e:
            logger.error(f"System Ingestion Failed. Agent running in Partial State. Error: {e}")

    async def check_db_state(self) -> bool:
        """
        Returns True if the Database appears to be fully populated (Sovereign).
        Checks for multiple critical signals, not just one key.
        """
        try:
            # 1. Critical Config Keys
            # Must have at least one provider key and one model definition
            # We check for a list of candidates.
            critical_keys = ["OPENAI_API_KEY", "AGENT_MODEL", "ROUTER_MODEL"]
            
            # Count how many critical keys exist
            # This query counts config_state rows where key matches any critical key
            q = f"SELECT count() FROM config_state WHERE key IN {json.dumps(critical_keys)} GROUP ALL"
            res = await run_query_with_memory(self.memory, q)
            
            # We expect at least 2 keys (e.g. API KEY + MODEL) to consider it "Configured"
            config_ok = False
            if res and res[0]['count'] >= 2:
                config_ok = True
                
            # 2. Hardware/System State
            # Must have at least one system record (e.g. 'hardware')
            res_sys = await run_query_with_memory(self.memory, "SELECT count() FROM system_state WHERE item = 'hardware' GROUP ALL")
            sys_ok = False
            if res_sys and res_sys[0]['count'] > 0:
                sys_ok = True
            
            if config_ok and sys_ok:
                logger.info("Bootstrap Integrity Check: PASSED (Config+System present).")
                return True
            else:
                logger.info(f"Bootstrap Integrity Check: FAILED (Config={config_ok}, System={sys_ok}). Triggering Ingestion.")
                return False
                
        except Exception as e:
            logger.warning(f"Bootstrap Integrity Check Exception: {e}")
            return False
        except Exception as e:
            logger.error(f"System Ingestion Failed: {e}")

    async def ingest_env(self):
        """Ingests .env variables."""
        env_path = os.path.join(self.fs_root, ".env")
        logger.info(f"DEBUG INGESTOR: fs_root={self.fs_root}, env_path={env_path}, exists={os.path.exists(env_path)}")
        
        if not os.path.exists(env_path):
            # Fallback to CWD
            cwd_env = os.path.join(os.getcwd(), ".env")
            logger.info(f"DEBUG INGESTOR: Fallback to CWD: {cwd_env}, exists={os.path.exists(cwd_env)}")
            if os.path.exists(cwd_env):
                env_path = cwd_env
            else:
                logger.warning(f".env not found at {env_path} or {cwd_env}")
                return

        logger.info(f"Ingesting .env from {env_path}")
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'").strip('"')
                    
                    # Store in DB
                    await self._store_config(key, val, "env")
        except Exception as e:
            logger.error(f"Failed to ingest .env: {e}")

    async def ingest_config(self):
        """Ingests config.yaml."""
        config_path = os.path.join(self.fs_root, "config.yaml")
        if not os.path.exists(config_path):
            return

        logger.info(f"Ingesting config.yaml from {config_path}")
        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
                # Flatten dictionary? Or store as JSON blob?
                # For now, let's flatten top-level keys
                for k, v in data.items():
                    val_str = json.dumps(v, default=str)
                    await self._store_config(k, val_str, "yaml")
        except Exception as e:
            logger.error(f"Failed to ingest config.yaml: {e}")

    async def ingest_system_profiler(self):
        """Ingests System Hardware and Software using system_profiler."""
        logger.info("Ingesting System Profiler Data...")
        # Subset of useful data types
        data_types = ["SPHardwareDataType", "SPApplicationsDataType", "SPNetworkDataType"]
        
        for dt in data_types:
            try:
                # Run command (Async via subprocess)
                # Note: SPApplicationsDataType can be HUGE. Maybe skip or limit?
                # Limiting to Hardware and Network for now to be safe on latency.
                if dt == "SPApplicationsDataType":
                    continue # Too slow for startup right now

                proc = await asyncio.create_subprocess_exec(
                    "system_profiler", dt, "-json",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                
                if proc.returncode != 0:
                    logger.warning(f"system_profiler {dt} failed: {stderr.decode()}")
                    continue

                data = json.loads(stdout.decode())
                # Handle the root key (usually matches datatype name)
                if dt in data:
                    items = data[dt]
                    # Collapse list if single item (Hardware)
                    if isinstance(items, list) and len(items) == 1:
                        cat = "Hardware" if "Hardware" in dt else "Network"
                        await self._store_system_state("hardware" if "Hardware" in dt else "network", items[0], category=cat)
                    else:
                        cat = "Network" if "Network" in dt else "System"
                        # [FIX] Schema Enforcement: 'details' must be an object, not a list.
                        if isinstance(items, list):
                            items = {"items": items}
                        await self._store_system_state(dt, items, category=cat)
                
            except Exception as e:
                logger.error(f"Failed to ingest {dt}: {e}")

    async def _store_config(self, key: str, value: str, source: str):
        """Helper to UPSERT config."""
        q = """
        UPSERT type::thing('config_state', $key) 
        SET key = $key, value = $val, source = $src, last_updated = time::now();
        """
        await run_query_with_memory(self.memory, q, {"key": key, "val": value, "src": source})

    async def _store_system_state(self, item: str, details: Any, category: str = "General"):
        """Helper to UPSERT system state."""
        q = """
        UPSERT type::thing('system_state', $item) 
        SET item = $item, details = $det, category = $cat, last_updated = time::now();
        """
        await run_query_with_memory(self.memory, q, {"item": item, "det": details, "cat": category})

    async def ingest_task_definitions(self):
        """
        Scan task definitions (YAML) on disk and ingest into 'task_def' table.
        This ensures DB has the latest code/config for tasks.
        """
        try:
            task_dir = Path(__file__).parent / "tasks" / "definitions"
            if not task_dir.exists():
                return
            
            logger.info(f"Scanning for Task Definitions in {task_dir}...")
            
            tasks_found = 0
            for yaml_file in task_dir.glob("*.yaml"):
                try:
                    with open(yaml_file, "r") as f:
                        data = yaml.safe_load(f)
                    
                    if not data or "name" not in data:
                        continue
                        
                    task_name = data["name"]
                    
                    # Construct record
                    record = {
                        "name": task_name,
                        "type": data.get("type", "agent"),
                        "enabled": data.get("enabled", True),
                        "schedule": str(data.get("schedule", "300")),
                        "idle_only": data.get("idle_only", False),
                        "priority": str(data.get("priority", "low")),
                        "description": data.get("description", ""),
                        "prompt": data.get("prompt", ""),
                        "config": data # Store full blob for extra fields
                    }
                    
                    # UPSERT: "DELETE then CREATE" logic to ensure clean slate for this ID
                    await run_query_with_memory(
                        self.memory,
                        "DELETE FROM task_def WHERE name = $name",
                        {"name": task_name}
                    )
                    await run_query_with_memory(
                        self.memory,
                        "CREATE task_def CONTENT $data",
                        {"data": record}
                    )
                    
                    tasks_found += 1
                except Exception as e:
                    logger.error(f"Failed to ingest task {yaml_file}: {e}")
            
            if tasks_found > 0:
                logger.info(f"Ingested {tasks_found} Task Definitions into Sovereign Memory.")
                
        except Exception as e:
            logger.error(f"Failed to ingest tasks: {e}")

    async def ingest_mcp_servers(self):
        """
        Scan MCP configuration (YAML/Manifests) and ingest into 'mcp_server' table.
        """
        try:
            # 1. Load from Manifests
            manifest_dir = Path(__file__).parent.parent / "config" / "mcp_manifests"
            if manifest_dir.exists():
                for m_file in manifest_dir.glob("*.json"):
                    try:
                        with open(m_file, "r") as f:
                            data = json.load(f)
                            servers = data.get("mcpServers", data)
                            for name, cfg in servers.items():
                                await self._upsert_mcp_server(name, cfg)
                    except Exception as e:
                        logger.error(f"Failed to ingest manifest {m_file}: {e}")

            # 2. Load from mcp.yaml
            mcp_yaml = Path(__file__).parent.parent / "config" / "mcp.yaml"
            if mcp_yaml.exists():
                try:
                    with open(mcp_yaml, "r") as f:
                        data = yaml.safe_load(f)
                        if data and "mcp_servers" in data:
                            for name, cfg in data["mcp_servers"].items():
                                await self._upsert_mcp_server(name, cfg)
                except Exception as e:
                    logger.error(f"Failed to ingest mcp.yaml: {e}")

            logger.info("Ingested MCP Servers into Sovereign Memory.")
            
        except Exception as e:
            logger.error(f"Failed to ingest MCP servers: {e}")

    async def _upsert_mcp_server(self, name: str, config: Dict[str, Any]):
        """Helper to upsert a single MCP server record."""
        # Normalize Command
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
        await run_query_with_memory(
            self.memory,
            f"DELETE FROM mcp_server WHERE name = '{name}'; CREATE mcp_server CONTENT $data",
            {"data": record}
        )

    async def ingest_registry(self):
        """
        Ingests the Sovereign Registry (sovereign.yaml) into the Database.
        This provides the baseline configuration for Models, Network, and Policies.
        """
        registry_path = os.path.join(os.path.dirname(os.path.dirname(self.fs_root)), "config", "sovereign.yaml")
        # Fallback if fs_root structure is different
        if not os.path.exists(registry_path):
             registry_path = os.path.join(self.fs_root, "config", "sovereign.yaml")
        
        if not os.path.exists(registry_path):
            logger.warning(f"Sovereign Registry not found at {registry_path}. Skipping.")
            return

        logger.info(f"Ingesting Sovereign Registry from {registry_path}...")
        try:
            with open(registry_path, "r") as f:
                data = yaml.safe_load(f) or {}

            # 1. MODELS
            models = data.get("models", {})
            for key, val in models.items():
                await self._upsert_registry_item("registry_models", key, val, "sovereign.yaml")

            # 2. NETWORK
            network = data.get("network", {})
            for key, val in network.items():
                 await self._upsert_registry_item("registry_ports", key, val, "sovereign.yaml")

            # 3. POLICIES
            policies = data.get("policies", {})
            for key, val in policies.items():
                 await self._upsert_registry_item("registry_policies", key, val, "sovereign.yaml")

            # 4. MCP
            mcp = data.get("mcp", {})
            for key, val in mcp.items():
                # MCP logic is slightly complex, it has 'enabled', 'command', etc.
                # We store the full blob.
                await self._upsert_registry_item("registry_mcp", key, json.dumps(val, default=str), "sovereign.yaml")

            logger.info("Sovereign Registry Ingestion Complete.")

        except Exception as e:
            logger.error(f"Failed to ingest Sovereign Registry: {e}")

    async def _upsert_registry_item(self, table: str, key: str, value: Any, source: str):
        """Helper to UPSERT registry items."""
        q = f"""
        UPSERT type::thing($table, $key) 
        SET key = $key, value = $val, source = $src, last_updated = time::now();
        """
        await run_query_with_memory(self.memory, q, {"table": table, "key": key, "val": value, "src": source})

    async def _upsert_mcp_server(self, name: str, config: Dict[str, Any]):
        # Legacy helper kept for clean diff execution if needed, but largely replaced by ingest_registry handling mcp blob
        # Actually we should keep it if we want 'mcp_server' specific table structure vs generic 'registry_mcp'
        # For unification, let's use the generic helper for now, or adapt this.
        # The prompt implies replacing the old manual mcp ingestion.
        # Let's map the old logic to the new `registry_mcp` table or keep `mcp_server` table but populated from sovereign?
        pass # Using generic `registry_mcp` for now as per plan.

    # [REMOVED: ingest_mcp_servers as it is now part of ingest_registry]

    async def ingest_permanent_memory(self):
        """
        Recursively scan BRAIN_DIR and sync all markdown files as sovereign memories.
        """
        if not self.brain_dir.exists():
            logger.warning(f"BRAIN_DIR not found at {self.brain_dir}. Skipping Sovereign Sync.")
            return

        logger.info(f"Scanning Sovereign Memory in {self.brain_dir}...")
        count = 0
        
        # Recursive glob
        for md_file in self.brain_dir.rglob("*.md"):
            try:
                # Derive stable ID (relative path without extension)
                # e.g. /Brain/Permanent_Memory/system/lexicon.md -> system/lexicon
                rel_path = md_file.relative_to(self.brain_dir)
                kb_id = str(rel_path.with_suffix('')) 
                
                # Check timestamps (Optimization: Only sync if changed)
                try:
                    stats = md_file.stat()
                    disk_mtime = stats.st_mtime
                    
                    db_time_str = await self.memory.check_sovereign_state(kb_id)
                    if db_time_str:
                        # Parse DB time (ISO format) to timestamp
                        # Using basic string comparison or proper parsing if needed.
                        # Surreal returns ISO string. 
                        # To be safe, if parse fails, we force sync.
                        import datetime
                        db_dt = datetime.datetime.fromisoformat(db_time_str.replace('Z', '+00:00'))
                        db_ts = db_dt.timestamp()
                        
                        # If Disk is older or equal to DB, skip
                        # Use a small buffer (e.g. 1s) for float variance
                        if disk_mtime <= (db_ts + 1.0):
                            # logger.debug(f"Skipping {kb_id}: Up to date.")
                            continue
                except Exception as te:
                    logger.warning(f"Timestamp check failed for {kb_id}, forcing sync: {te}")

                # Use async file I/O
                import aiofiles
                async with aiofiles.open(md_file, "r") as f:
                    content = await f.read()
                
                if not content.strip(): continue

                # Perform Atomic Sync (Wipe & Replace)
                res = await self.memory.sync_sovereign_file(kb_id, content)
                if res.get("ok"):
                    count += 1
            except Exception as e:
                logger.error(f"Failed to sync sovereign file {md_file}: {e}")

        logger.info(f"Sovereign Memory Sync Complete: {count} files synced.")

    async def ingest_project_registry(self):
        """
        Recursively scan data/permanent/ directory and sync all markdown files as project registry.
        These are project-specific context files (e.g., user_profile.md, inventory.md).
        """
        registry_dir = Path(self.fs_root) / "data" / "permanent"
        if not registry_dir.exists():
            logger.debug(f"Project registry directory not found at {registry_dir}. Skipping.")
            return

        logger.info(f"Scanning Project Registry in {registry_dir}...")
        count = 0
        
        # Recursive glob
        for md_file in registry_dir.rglob("*.md"):
            try:
                # Derive stable ID (relative path without extension)
                # e.g. data/permanent/user_profile.md -> project_registry/user_profile
                rel_path = md_file.relative_to(registry_dir)
                kb_id = f"project_registry/{str(rel_path.with_suffix(''))}"
                
                # Check timestamps (Optimization: Only sync if changed)
                try:
                    stats = md_file.stat()
                    disk_mtime = stats.st_mtime
                    
                    db_time_str = await self.memory.check_sovereign_state(kb_id)
                    if db_time_str:
                        import datetime
                        db_dt = datetime.datetime.fromisoformat(db_time_str.replace('Z', '+00:00'))
                        db_ts = db_dt.timestamp()
                        
                        # If Disk is older or equal to DB, skip
                        if disk_mtime <= (db_ts + 1.0):
                            continue
                except Exception as te:
                    logger.warning(f"Timestamp check failed for {kb_id}, forcing sync: {te}")

                # Use async file I/O
                import aiofiles
                async with aiofiles.open(md_file, "r") as f:
                    content = await f.read()
                
                if not content.strip(): continue

                # Perform Atomic Sync (Wipe & Replace)
                res = await self.memory.sync_sovereign_file(kb_id, content)
                if res.get("ok"):
                    count += 1
            except Exception as e:
                logger.error(f"Failed to sync project registry file {md_file}: {e}")

        logger.info(f"Project Registry Sync Complete: {count} files synced.")
