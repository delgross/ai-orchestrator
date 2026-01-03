import os
import json
import yaml
import logging
import asyncio
from typing import Any, Optional, Dict
from pathlib import Path

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    The Authority for Configuration Changes.
    Ensures that changes are propagated to:
    1. Sovereign Memory (SurrealDB) - The Master.
    2. Runtime State (RAM/Env) - The Active Cache.
    3. Cold Storage (Disk) - The Backup.
    """
    def __init__(self, state: AgentState):
        self.state = state
        self.memory = MemoryServer(state)
        # We assume MemoryServer is already connected via state initialization
    async def check_and_sync_all(self):
        """
        Boot-time check: Sync all config files if disk is newer than DB.
        """
        logger.info("Performing Sovereign File Sync Check...")
        
        # 1. config.yaml
        await self._sync_if_newer(
            self.state.agent_fs_root.parent / "config" / "config.yaml",
            "config_yaml",
            self.sync_base_config_from_disk
        )

        # 2. mcp.yaml
        await self._sync_if_newer(
            self.state.agent_fs_root.parent / "config" / "mcp.yaml",
            "mcp_yaml",
            self.sync_mcp_from_disk
        )
        
        # 3. .env
        await self._sync_if_newer(
            self.state.agent_fs_root.parent / ".env",
            "env_file",
            self.sync_env_from_disk
        )

        # 4. system_config.json
        await self._sync_if_newer(
            self.state.agent_fs_root.parent / "system_config.json",
            "system_config",
            self.sync_from_disk
        )
        
    async def _sync_if_newer(self, file_path: Path, meta_key: str, sync_method) -> bool:
        """
        Checks mtime of file vs 'meta:{meta_key}_mtime' in DB.
        If file is newer, awaits sync_method() and updates DB timestamp.
        """
        if not file_path.exists():
            return False
            
        try:
            # 1. Get Disk mtime
            disk_mtime = file_path.stat().st_mtime
            
            # 2. Get DB mtime
            db_key = f"meta:{meta_key}_mtime"
            q = "SELECT value FROM config_state WHERE key = $key"
            res = await self.memory._execute_query(q, {"key": db_key})
            
            db_mtime = 0.0
            if res and len(res) > 0:
                try:
                    db_mtime = float(res[0].get("value", 0.0))
                except:
                    pass
            
            # 3. Compare (Use a small epsilon for float equality or just strict greater)
            # If disk is newer by at least 1 second (file systems vary)
            if disk_mtime > db_mtime + 0.001:
                logger.info(f"Sovereign Sync: {file_path.name} (Disk {disk_mtime}) > (DB {db_mtime}). Syncing...")
                
                # Execute specific sync logic
                await sync_method()
                
                # Update DB Timestamp
                await self._update_db_config(db_key, str(disk_mtime), "file_watcher")
                return True
                
            return False
        except Exception as e:
            logger.error(f"Sovereign Sync Check failed for {file_path.name}: {e}")
            return False
        """
        Update a Secret (API Key, Token).
        Target: .env (Backup), config_state (Master), os.environ (Runtime)
        """
        logger.info(f"Updating Secret: {key}...")
        
        # 1. Update Sovereign Memory
        try:
            await self._update_db_config(key, value, "env")
        except Exception as e:
            logger.error(f"Failed to update Secret in DB: {e}")
            return False

        # 2. Update Runtime
        os.environ[key] = str(value)
        
        # Update AgentState attributes if mapped
        self._update_state_attributes(key, value)
        
        # 3. Update Disk Backup (.env)
        try:
            await self._patch_env_file(key, value)
        except Exception as e:
            logger.error(f"Failed to patch .env file: {e}")
            # We don't return False here because logic flow (DB/Runtime) succeeded.
            # We just log the backup failure.
        
        return True

    async def set_config_value(self, key: str, value: Any) -> bool:
        """
        Update a Configuration Value (Model, Timeout, etc).
        Target: system_config.json (Backup), config_state (Master), AgentState (Runtime)
        """
        logger.info(f"Updating Config: {key} -> {value}")
        
        # 1. Update Sovereign Memory
        try:
            await self._update_db_config(key, value, "api")
        except Exception as e:
            logger.error(f"Failed to update Config in DB: {e}")
            return False

        # 2. Update Runtime
        self._update_state_attributes(key, value)
        
        # 3. Update Disk Backup (system_config.json)
        try:
            config_path = self.state.agent_fs_root.parent / "system_config.json"
            cfg = {}
            if config_path.exists():
                with open(config_path, "r") as f:
                    cfg = json.load(f)
            
            # Use lowercase for json compatibility usually, but state attributes are mapped from UPPER.
            # system_config.json typically uses lowercase keys (e.g. "vision_model").
            # Let's map UPPER -> lower for file storage if it matches standard keys.
            file_key = key.lower()
            cfg[file_key] = value
            
            with open(config_path, "w") as f:
                json.dump(cfg, f, indent=4)
                
            logger.info(f"Backed up {key} to {config_path}")
        except Exception as e:
            logger.error(f"Failed to patch system_config.json: {e}")
        
        return True

    async def _update_db_config(self, key: str, value: Any, source: str):
        """UPSERT into config_state table."""
        q = """
        UPSERT type::thing('config_state', $key) 
        SET key = $key, value = $val, source = $src, last_updated = time::now();
        """
        # Ensure values are strings for simple KV storage, or handle JSON if needed.
        # For secrets/config, string is usually safe.
        val_str = str(value) if not isinstance(value, (int, float, bool)) else value
        await self.memory._execute_query(q, {"key": key, "val": val_str, "src": source})

    def _update_state_attributes(self, key: str, value: Any):
        """Reflect changes in AgentState object immediately."""
        # Map well-known keys to attributes
        if key == "AGENT_MODEL": self.state.agent_model = value
        elif key == "ROUTER_MODEL": self.state.router_model = value
        elif key == "TASK_MODEL": self.state.task_model = value
        elif key == "VISION_MODEL": self.state.vision_model = value
        elif key == "EMBEDDING_MODEL": self.state.embedding_model = value
        elif key == "MCP_MODEL": self.state.mcp_model = value
        elif key == "SUMMARIZATION_MODEL": self.state.summarization_model = value
        elif key == "FINALIZER_MODEL": self.state.finalizer_model = value
        elif key == "FALLBACK_MODEL": self.state.fallback_model = value
        elif key == "INTENT_MODEL": self.state.intent_model = value
        elif key == "PRUNER_MODEL": self.state.pruner_model = value
        elif key == "HEALER_MODEL": self.state.healer_model = value
        elif key == "CRITIC_MODEL": self.state.critic_model = value
        # Add more mappings as needed

    async def _patch_env_file(self, key: str, value: str):
        """
        Safely update a key in .env using Regex to handle quotes/comments.
        Example: 
          KEY="Old" # Comment -> KEY="New" # Comment
        """
        import re
        
        env_path = self.state.agent_fs_root / ".env"
        # Fallback if fs_root is bad (logic we added to ingestor, let's replicate or assume fix)
        if not env_path.exists():
            env_path = Path(os.getcwd()) / ".env"
            
        if not env_path.exists():
            # Create new if missing
            logger.warning("Creating new .env file for backup.")
            with open(env_path, "w") as f:
                f.write(f'{key}="{value}"\n')
            return

        # Read all lines
        lines = []
        with open(env_path, "r") as f:
            lines = f.readlines()

        key_found = False
        new_lines = []
        
        # Regex: Start of line, Optional export, KEY, Optional WS, =, Optional WS, Capture Value, Optional WS, Optional Comment
        # Actually simpler: Just find the key assignment and replace the value part
        # ^(export\s+)?KEY\s*=.*
        pattern = re.compile(rf'^(?:export\s+)?{re.escape(key)}\s*=.*', re.MULTILINE)
        
        updated_line = f'{key}="{value}"'

        for line in lines:
            if pattern.match(line):
                # Preserve comment if exists
                if "#" in line:
                    comment = line.split("#", 1)[1].rstrip()
                    new_lines.append(f'{updated_line} # {comment}\n')
                else:
                    new_lines.append(f'{updated_line}\n')
                key_found = True
            else:
                new_lines.append(line)
        
        if not key_found:
            # Append to end
            if new_lines and not new_lines[-1].endswith("\n"):
                new_lines.append("\n")
            new_lines.append(f'{updated_line}\n')

        # Atomic Write
        tmp_path = env_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            f.writelines(new_lines)
        
        os.rename(tmp_path, env_path)
        logger.info(f"Backed up {key} to {env_path}")

    # Future: set_preference(key, val) -> system_config.json
    # Future: set_preference(key, val) -> system_config.json
    
    async def save_mcp_config(self, servers: Dict[str, Any]) -> bool:
        """
        Save MCP Server configuration to disk (Atomic).
        Used by add/remove/toggle operations.
        """
        config_path = self.state.agent_fs_root.parent / "config" / "mcp.yaml" # ~/ai/config/mcp.yaml
        if not config_path.parent.exists():
            # Try relative path backup if fs_root structure differs
             config_path = Path(__file__).parent.parent / "config" / "mcp.yaml"

        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 1. Load existing to preserve comments/structure? 
            # YAML libraries usually kill comments.
            # We will overwrite with the authoritative state.
            
            data = {"mcp_servers": servers}
            
            # 2. Atomic Write
            tmp_path = config_path.with_suffix(".tmp")
            with open(tmp_path, "w") as f:
                 yaml.dump(data, f, sort_keys=False, indent=2)
            
            os.rename(tmp_path, config_path)
            logger.info(f"Saved MCP config to {config_path}")
            
            # 3. Sync to DB (Best Effort)
            # In a full Sovereign model, we might want to update DB here too,
            # ensuring Runtime -> Disk -> DB flow is consistent.
            # But usually it's Runtime -> DB -> Disk.
            return True
        except Exception as e:
            logger.error(f"Failed to save MCP config: {e}")
            return False

    async def update_mcp_server(self, name: str, config: Dict[str, Any]):
        """
        Update a single MCP server in Sovereign Memory and Disk.
        """
        # 1. Update DB (Sovereign)
        # Prepare record
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
        
        q = "UPSERT mcp_server CONTENT $data"
        await self.memory._execute_query(f"DELETE FROM mcp_server WHERE name = '{name}'; {q}", {"data": record})
        
        # 2. Update Disk (Reverse Sync) via full dump of state.mcp_servers
        # We assume state.mcp_servers has been updated by the caller (AgentState)
        # OR we wait for AgentState to call us.
        # Ideally ConfigManager should be the entry point.
        # But for refactoring `state.py`, let's expose the disk save.
        pass # The caller will call save_mcp_config with the full list.

    async def save_task_definition(self, task_name: str, task_data: Dict[str, Any]) -> bool:
        """
        Reverse Sync: Save a task definition from Memory/Runtime back to Disk (YAML).
        Used when admin tools update a task in the DB.
        """
        try:
            # 1. Validate inputs
            if not task_name or not task_data:
                return False
                
            # 2. Construct File Path
            # Defined in system_ingestor as well, let's keep consistent
            task_dir = Path(__file__).parent / "tasks" / "definitions"
            task_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = task_dir / f"{task_name}.yaml"
            
            # 3. Clean Data for YAML
            # Remove DB specific fields if any, or internal IDs
            output_data = {
                "name": task_data.get("name"),
                "type": task_data.get("type", "agent"),
                "enabled": task_data.get("enabled", True),
                "schedule": task_data.get("schedule", "300"),
                "idle_only": task_data.get("idle_only", False),
                "priority": task_data.get("priority", "low"),
                "description": task_data.get("description", ""),
                "prompt": task_data.get("prompt", "")
            }
            # Add back extra config items that might be in 'config' blob or root
            if "config" in task_data and isinstance(task_data["config"], dict):
                # Merge extras like 'tools', 'output_file'
                for k, v in task_data["config"].items():
                    if k not in output_data:
                        output_data[k] = v
                        
            # Normalize schedule (DB might return string "300", we want int/string as is)
            
            # 4. Write YAML (Atomic)
            tmp_path = file_path.with_suffix(".tmp")
            with open(tmp_path, "w") as f:
                yaml.dump(output_data, f, sort_keys=False, default_flow_style=False)
            
            os.rename(tmp_path, file_path)
                
            logger.info(f"Reverse Sync: Saved task '{task_name}' to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reverse sync task {task_name}: {e}")
            return False

    def start_watcher(self):
        """
        Starts the Config Watcher to monitor system_config.json for changes.
        This enables 'Hot Swap' capability.
        """
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class ConfigHandler(FileSystemEventHandler):
                def __init__(self, manager):
                    self.manager = manager
                    # self.last_ts not needed, using mtime checks

                def on_modified(self, event):
                    filename = Path(event.src_path).name
                    # Using _sync_if_newer handles debouncing via timestamp comparison
                    
                    if filename == "system_config.json":
                        asyncio.run_coroutine_threadsafe(
                            self.manager._sync_if_newer(
                                Path(event.src_path), "system_config", self.manager.sync_from_disk
                            ), 
                            self.manager.state.loop
                        )

                    elif filename == ".env":
                        asyncio.run_coroutine_threadsafe(
                            self.manager._sync_if_newer(
                                Path(event.src_path), "env_file", self.manager.sync_env_from_disk
                            ),
                            self.manager.state.loop
                        )

                    elif filename == "config.yaml":
                        asyncio.run_coroutine_threadsafe(
                             self.manager._sync_if_newer(
                                Path(event.src_path), "config_yaml", self.manager.sync_base_config_from_disk
                             ),
                             self.manager.state.loop
                        )

                    elif filename == "mcp.yaml":
                         asyncio.run_coroutine_threadsafe(
                             self.manager._sync_if_newer(
                                Path(event.src_path), "mcp_yaml", self.manager.sync_mcp_from_disk
                             ),
                             self.manager.state.loop
                        )

            # Determine paths to watch
            root_dir = self.state.agent_fs_root.parent
            config_dir = root_dir / "config"
            
            observer = Observer()
            handler = ConfigHandler(self)
            
            # Watch Root for system_config.json and .env
            observer.schedule(handler, str(root_dir), recursive=False)
            
            # Watch Config Dir for config.yaml and mcp.yaml
            if config_dir.exists():
                observer.schedule(handler, str(config_dir), recursive=False)
            
            observer.start()
            logger.info(f"Sovereign Config Watcher started on {root_dir} and {config_dir}")
            
            self.observer = observer

        except ImportError:
            logger.warning("Watchdog not installed. Config Hot-Swap disabled.")
        except Exception as e:
            logger.error(f"Failed to start Config Watcher: {e}")

    async def sync_from_disk(self):
        """
        Reads system_config.json from disk and updates DB + Runtime.
        Triggered by Watchdog.
        """
        config_path = self.state.agent_fs_root.parent / "system_config.json"
        
        if not config_path.exists():
            return

        logger.info("Syncing Config from Disk to Sovereign Memory...")
        try:
            with open(config_path, "r") as f:
                cfg = json.load(f)
                
            # Iterate and Upsert to DB
            for key, val in cfg.items():
                # Store in DB
                await self._update_db_config(key.upper(), val, "hot_swap")
                # Update Runtime immediately
                self._update_state_attributes(key.upper(), val)
                
            logger.info("Config Sync Complete. Runtime State Updated.")
            
        except Exception as e:
            logger.error(f"Config Sync Failed: {e}")

    async def sync_env_from_disk(self):
        """Syncs .env changes to Sovereign Memory (Secrets)."""
        env_path = self.state.agent_fs_root.parent / ".env"
        if not env_path.exists(): return
        
        logger.info("[Watcher] Syncing .env to Sovereign Memory...")
        try:
            import dotenv
            # Load without touching os.environ yet
            values = dotenv.dotenv_values(env_path)
            
            for key, val in values.items():
                if val:
                    # Update DB (Source=env)
                    await self._update_db_config(key, val, "env")
                    # Update Runtime
                    os.environ[key] = val
                    self._update_state_attributes(key, val)
                    
            logger.info("[Watcher] .env Sync Complete.")
        except Exception as e:
            logger.error(f"Failed to sync .env: {e}")

    async def sync_base_config_from_disk(self):
        """Syncs config.yaml changes to Sovereign Memory (Base Config)."""
        config_path = self.state.agent_fs_root.parent / "config" / "config.yaml"
        if not config_path.exists(): return

        logger.info("[Watcher] Syncing config.yaml to Sovereign Memory...")
        try:
            with open(config_path, "r") as f:
                cfg = yaml.safe_load(f) or {}

            # We flatten critical keys for the DB or store as JSON blob?
            # Creating a 'base_config' entry might be cleaner, but user wants granular overrides.
            # For now, we allow high-level keys to update runtime attributes.
            
            for key, val in cfg.items():
                # We trust config.yaml structure matches some internal expectation
                # Update DB (Source=config_yaml)
                await self._update_db_config(key.upper(), val, "config_yaml")
                # Update Runtime
                self._update_state_attributes(key.upper(), val)
                
            logger.info("[Watcher] config.yaml Sync Complete.")
        except Exception as e:
            logger.error(f"Failed to sync config.yaml: {e}")

    async def sync_mcp_from_disk(self):
        """Syncs mcp.yaml changes to Sovereign Memory (MCP Servers)."""
        mcp_path = self.state.agent_fs_root.parent / "config" / "mcp.yaml"
        if not mcp_path.exists(): return

        logger.info("[Watcher] Syncing mcp.yaml to Sovereign Memory...")
        try:
            with open(mcp_path, "r") as f:
                data = yaml.safe_load(f) or {}
                
            servers = data.get("mcp_servers", {})
            for name, config in servers.items():
                # Re-use update logic but ensure we don't write back to disk
                # calling update_mcp_server updates DB.
                # update_mcp_server current impl has `pass` for disk write, so it is safe.
                await self.update_mcp_server(name, config)
                
            logger.info(f"[Watcher] mcp.yaml Sync Complete ({len(servers)} servers updated).")
        except Exception as e:
            logger.error(f"Failed to sync mcp.yaml: {e}")
