import os
import json
import yaml
import logging
import asyncio
from typing import Any, Optional, Dict
from pathlib import Path

from agent_runner.state import AgentState
from agent_runner.memory_server import MemoryServer
from agent_runner.db_utils import run_query

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
        Executes checks in PARALLEL to reduce startup latency.
        
        [PHASE 3] Optimization: Fetch mtimes in batch along with hashes for fast-path check.
        """
        logger.info("Performing Sovereign File Sync Check (Parallel)...")
        
        # [OPTIMIZATION] Batch fetch all hashes AND mtimes to avoid sequential DB round-trips
        # This resolves the bottleneck where asyncio.gather was serialized by DB lock contention.
        keys = [
            # Hashes
            "meta:config_yaml_hash",
            "meta:mcp_yaml_hash",
            "meta:env_file_hash",
            "meta:system_config_hash",
            "meta:sovereign_config_hash",
            # [PHASE 3] MTimes for fast-path check
            "meta:config_yaml_mtime",
            "meta:mcp_yaml_mtime",
            "meta:env_file_mtime",
            "meta:system_config_mtime",
            "meta:sovereign_config_mtime"
        ]
        # Format for SurrealQL: ['key1', 'key2', ...]
        formatted_keys = "[" + ", ".join([f"'{k}'" for k in keys]) + "]" 
        q = f"SELECT * FROM config_state WHERE key IN {formatted_keys}"
        
        try:
            res = await run_query(self.state, q)
            # Map key -> value
            db_cache = {r['key']: str(r['value']) for r in res} if res else {}
        except Exception as e:
            logger.warning(f"Batch metadata fetch failed: {e}. Falling back to empty.")
            db_cache = {}
            
        # Define tasks with pre-fetched hashes and mtimes
        tasks = [
            # 1. config.yaml
            self._sync_if_newer(
                self.state.agent_fs_root.parent / "config" / "config.yaml",
                "config_yaml",
                self.sync_base_config_from_disk,
                pre_fetched_hash=db_cache.get("meta:config_yaml_hash", ""),
                pre_fetched_mtime=db_cache.get("meta:config_yaml_mtime", None)
            ),
            # 2. mcp.yaml
            self._sync_if_newer(
                self.state.agent_fs_root.parent / "config" / "mcp.yaml",
                "mcp_yaml",
                self.sync_mcp_from_disk,
                pre_fetched_hash=db_cache.get("meta:mcp_yaml_hash", ""),
                pre_fetched_mtime=db_cache.get("meta:mcp_yaml_mtime", None)
            ),
            # 3. .env
            self._sync_if_newer(
                self.state.agent_fs_root.parent / ".env",
                "env_file",
                self.sync_env_from_disk,
                pre_fetched_hash=db_cache.get("meta:env_file_hash", ""),
                pre_fetched_mtime=db_cache.get("meta:env_file_mtime", None)
            ),
            # 4. system_config.json
            self._sync_if_newer(
                self.state.agent_fs_root.parent / "system_config.json",
                "system_config",
                self.sync_from_disk,
                pre_fetched_hash=db_cache.get("meta:system_config_hash", ""),
                pre_fetched_mtime=db_cache.get("meta:system_config_mtime", None)
            ),
            # 5. sovereign.yaml (Master Config)
            self._sync_if_newer(
                self.state.agent_fs_root.parent / "config" / "sovereign.yaml",
                "sovereign_config",
                self.sync_sovereign_from_disk,
                pre_fetched_hash=db_cache.get("meta:sovereign_config_hash", ""),
                pre_fetched_mtime=db_cache.get("meta:sovereign_config_mtime", None)
            )
        ]

        # Execute all sync checks concurrently
        await asyncio.gather(*tasks)
        
    async def _sync_if_newer(self, file_path: Path, meta_key: str, sync_method, pre_fetched_hash: str = None, pre_fetched_mtime: str = None) -> bool:
        """
        Checks content hash of file vs 'meta:{meta_key}_hash' in DB.
        If content changed, awaits sync_method() and updates DB hash.
        Uses execution-time provided hash if available to save a query.
        
        [PHASE 3] Optimization: Use file mtime as fast-path check to avoid MD5 on every boot.
        """
        if not file_path.exists():
            return False
            
        try:
            import hashlib
            import os.path
            
            # [PHASE 3] FAST PATH: Check file modification time first
            # Only compute expensive MD5 if file mtime changed since last check
            mtime_key = f"meta:{meta_key}_mtime"
            current_mtime = os.path.getmtime(file_path)
            
            # Use pre-fetched mtime if available
            if pre_fetched_mtime is not None:
                cached_mtime = float(pre_fetched_mtime) if pre_fetched_mtime else 0.0
            else:
                # Fallback: Query DB for mtime
                mtime_query = "SELECT * FROM config_state WHERE key = $key"
                mtime_res = await run_query(self.state, mtime_query, {"key": mtime_key})
                cached_mtime = float(mtime_res[0].get("value", 0)) if mtime_res and len(mtime_res) > 0 else 0.0
            
            # If mtime hasn't changed, file is identical - skip hash computation
            if current_mtime == cached_mtime and cached_mtime > 0:
                logger.info(f"[PHASE 3] Fast-path HIT: {file_path.name} unchanged (mtime: {current_mtime})")
                return False
            else:
                logger.info(f"[PHASE 3] Fast-path MISS: {file_path.name} - mtime changed ({cached_mtime} -> {current_mtime})")
            
            # SLOW PATH: File changed (or first boot) - compute MD5 hash
            # 1. Compute file content hash
            with open(file_path, 'rb') as f:
                disk_hash = hashlib.md5(f.read()).hexdigest()
            
            # 2. Get DB hash (Use pre-fetched if available)
            if pre_fetched_hash is not None:
                db_hash = pre_fetched_hash
            else:
                db_key = f"meta:{meta_key}_hash"
                q = "SELECT * FROM config_state WHERE key = $key"
                logger.warning(f"[Watcher] Querying DB hash for {db_key}...")
                try:
                    res = await run_query(self.state, q, {"key": db_key})
                    db_hash = str(res[0].get("value", "")) if res and len(res) > 0 else ""
                    logger.warning(f"[Watcher] DB Hash: {db_hash[:8]}... Disk Hash: {disk_hash[:8]}...")
                except Exception as db_err:
                    logger.error(f"[Watcher] DB Hash Query Failed: {db_err}")
                    db_hash = "" # Force sync if DB fails? Or abort?
            
            # 3. Compare hashes (only sync if content actually changed)
            if disk_hash != db_hash:
                logger.warning(f"[Watcher] Hash Mismatch! Syncing {file_path.name}...")
                logger.info(f"Sovereign Sync: {file_path.name} content changed (hash: {disk_hash[:8]}...). Syncing...")
                
                # Execute specific sync logic
                await sync_method()
                
                # Update DB Hash AND mtime
                db_key = f"meta:{meta_key}_hash"
                await self._update_db_config(db_key, disk_hash, "file_watcher")
                await self._update_db_config(mtime_key, str(current_mtime), "file_watcher")
                logger.info(f"[PHASE 3] Saved mtime cache: {mtime_key} = {current_mtime}")
                return True
            else:
                # Hash unchanged but mtime changed (e.g., editor touch) - update mtime cache
                await self._update_db_config(mtime_key, str(current_mtime), "file_watcher")
                logger.debug(f"{file_path.name} mtime changed but content unchanged")
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
        Target: Database (Master), Runtime State, and ALL disk backups:
        - system_config.json
        - config/config.yaml
        - agent_runner/agent_runner.env (if it's a MODEL config)
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
        
        # 3. Update ALL Disk Backups (keep all files in sync)
        disk_update_errors = []
        
        # 3a. Update system_config.json
        try:
            config_path = self.state.agent_fs_root.parent / "system_config.json"
            cfg = {}
            if config_path.exists():
                with open(config_path, "r") as f:
                    cfg = json.load(f)
            
            # Use lowercase for json compatibility usually, but state attributes are mapped from UPPER.
            # system_config.json typically uses lowercase keys (e.g. "vision_model").
            file_key = key.lower()
            cfg[file_key] = value
            
            with open(config_path, "w") as f:
                json.dump(cfg, f, indent=4)
                
            logger.info(f"✅ Backed up {key} to {config_path}")
        except Exception as e:
            error_msg = f"Failed to patch system_config.json: {e}"
            logger.error(error_msg)
            disk_update_errors.append(error_msg)
        
        # 3b. Update config/config.yaml (if it's a model config)
        if key.endswith("_MODEL") or key in ["AGENT_MODEL", "ROUTER_MODEL", "TASK_MODEL", "VISION_MODEL", 
                                               "EMBEDDING_MODEL", "MCP_MODEL", "SUMMARIZATION_MODEL", 
                                               "FINALIZER_MODEL", "FALLBACK_MODEL", "INTENT_MODEL", 
                                               "PRUNER_MODEL", "HEALER_MODEL", "CRITIC_MODEL", 
                                               "QUERY_REFINEMENT_MODEL"]:
            try:
                yaml_path = self.state.agent_fs_root.parent / "config" / "config.yaml"
                if yaml_path.exists():
                    with open(yaml_path, "r") as f:
                        yaml_data = yaml.safe_load(f) or {}
                    
                    # Ensure 'system' section exists
                    if "system" not in yaml_data:
                        yaml_data["system"] = {}
                    
                    # Map UPPER key to lowercase for YAML (e.g., AGENT_MODEL -> agent_model)
                    yaml_key = key.lower()
                    yaml_data["system"][yaml_key] = value
                    
                    with open(yaml_path, "w") as f:
                        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                    
                    logger.info(f"✅ Backed up {key} to {yaml_path}")
                else:
                    logger.debug(f"config.yaml not found at {yaml_path}, skipping")
            except Exception as e:
                error_msg = f"Failed to patch config.yaml: {e}"
                logger.error(error_msg)
                disk_update_errors.append(error_msg)
        
        # 3c. Update agent_runner/agent_runner.env (if it's AGENT_MODEL)
        # Note: Only AGENT_MODEL is stored in agent_runner.env based on current file structure
        if key == "AGENT_MODEL":
            try:
                env_path = self.state.agent_fs_root.parent / "agent_runner" / "agent_runner.env"
                if env_path.exists():
                    await self._patch_agent_runner_env(key, str(value), env_path)
                    logger.info(f"✅ Backed up {key} to {env_path}")
                else:
                    logger.debug(f"agent_runner.env not found at {env_path}, skipping")
            except Exception as e:
                error_msg = f"Failed to patch agent_runner.env: {e}"
                logger.error(error_msg)
                disk_update_errors.append(error_msg)
        
        # Log summary
        if disk_update_errors:
            logger.warning(f"Some disk backups failed (non-critical): {len(disk_update_errors)} errors")
        else:
            logger.info(f"✅ All disk backups updated for {key}")
        
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
        await run_query(self.state, q, {"key": key, "val": val_str, "src": source})

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
        elif key == "QUERY_REFINEMENT_MODEL": self.state.query_refinement_model = value
        elif key == "ROUTER_AUTH_TOKEN": self.state.router_auth_token = value
        # Add more mappings as needed

    async def _patch_env_file(self, key: str, value: str):
        """
        Safely update a key in .env using python-dotenv.
        """
        try:
            import dotenv
        except ImportError:
            logger.error("python-dotenv library not found. Cannot update .env file.")
            return

        # Determine path - prefer project root (parent of agent_fs_root)
        env_path = self.state.agent_fs_root.parent / ".env"
        
        # Fallback to CWD if specific path doesn't exist (unless we want to force creation at specific path)
        if not env_path.exists():
            cwd_path = Path(os.getcwd()) / ".env"
            if cwd_path.exists():
                env_path = cwd_path
            
        # Create if missing (default to project root)
        if not env_path.exists():
            logger.warning(f"Creating new .env file at {env_path}")
            env_path.parent.mkdir(parents=True, exist_ok=True)
            env_path.touch()

        # set_key performs atomic-ish rewrite
        # We run it in a thread to avoid blocking the event loop (it does file I/O)
        def _update():
             # quote_mode='always' ensures complex strings/multiline are safe
             return dotenv.set_key(str(env_path), key, value, quote_mode="always")

        try:
            success, key_out, value_out = await asyncio.to_thread(_update)
            
            if success:
                 logger.info(f"Updated .env: {key}=*** at {env_path}")
            else:
                 logger.warning(f"Failed to update .env for {key} at {env_path}")
        except Exception as e:
            logger.error(f"Error updating .env file: {e}")



    async def _patch_agent_runner_env(self, key: str, value: str, env_path: Path):
        """
        Safely update a key in agent_runner/agent_runner.env using python-dotenv.
        """
        try:
            import dotenv
        except ImportError:
            logger.error("python-dotenv library not found.")
            return

        if not env_path.exists():
            logger.debug(f"agent_runner.env not found at {env_path}, skipping")
            return

        def _update():
             return dotenv.set_key(str(env_path), key, value, quote_mode="always")

        try:
            success, _, _ = await asyncio.to_thread(_update)
            if success:
                logger.info(f"Updated {env_path.name}: {key}=***")
            else:
                logger.warning(f"Failed to update {env_path.name}")
        except Exception as e:
            logger.error(f"Error updating {env_path.name}: {e}")


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
        
        # Include disabled_reason if present
        if "disabled_reason" in config:
            record["disabled_reason"] = config["disabled_reason"]
        

        q = "UPSERT mcp_server CONTENT $data"
        await run_query(self.state, f"DELETE FROM mcp_server WHERE name = '{name}'; {q}", {"data": record})
        
        # 2. Update Disk (Reverse Sync) via full dump of state.mcp_servers

        
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
                    # Track last known content hash to prevent false positives
                    self._last_hashes = {}

                def on_modified(self, event):
                    """Handle file modification events, but only sync if content actually changed."""
                    if event.is_directory:
                        return
                    
                    file_path = Path(event.src_path)
                    filename = file_path.name
                    
                    # Check if content actually changed (prevent false positives from file access/metadata)
                    try:
                        import hashlib
                        with open(file_path, 'rb') as f:
                            current_hash = hashlib.md5(f.read()).hexdigest()
                        
                        last_hash = self._last_hashes.get(str(file_path), "")
                        
                        # Only proceed if content actually changed
                        if current_hash == last_hash:
                            # Content didn't change - false positive (file access, metadata change, etc.)
                            return
                        
                        # Update last known hash
                        self._last_hashes[str(file_path)] = current_hash
                    except (OSError, AttributeError, IOError):
                        # File might not exist, be locked, or read failed - proceed with sync check
                        # _sync_if_newer will handle the actual hash comparison
                        pass
                    
                    # Using _sync_if_newer handles content hash comparison
                    target_loop = getattr(self.manager, "loop", None)
                    if target_loop is None:
                        try:
                            target_loop = asyncio.get_running_loop()
                        except RuntimeError:
                            target_loop = asyncio.get_event_loop_policy().get_event_loop()
                        self.manager.loop = target_loop
                    
                    if filename == "system_config.json":
                        asyncio.run_coroutine_threadsafe(
                            self.manager._sync_if_newer(
                                file_path, "system_config", self.manager.sync_from_disk
                            ), 
                            target_loop
                        )

                    elif filename == ".env":
                        asyncio.run_coroutine_threadsafe(
                            self.manager._sync_if_newer(
                                file_path, "env_file", self.manager.sync_env_from_disk
                            ),
                            target_loop
                        )

                    elif filename == "config.yaml":
                        asyncio.run_coroutine_threadsafe(
                             self.manager._sync_if_newer(
                                file_path, "config_yaml", self.manager.sync_base_config_from_disk
                             ),
                             target_loop
                        )

                    elif filename == "sovereign.yaml":
                         asyncio.run_coroutine_threadsafe(
                             self.manager._sync_if_newer(
                                file_path, "sovereign_config", self.manager.sync_sovereign_from_disk
                             ),
                             target_loop
                        )

            # Determine paths to watch
            root_dir = self.state.agent_fs_root.parent
            config_dir = root_dir / "config"
            
            # Capture the running loop for thread callbacks
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:
                self.loop = asyncio.get_event_loop_policy().get_event_loop()

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
        """Syncs .env changes to Sovereign Memory (Secrets) and PRUNES removed keys."""
        env_path = self.state.agent_fs_root.parent / ".env"
        if not env_path.exists(): return
        
        logger.info("[Watcher] Syncing .env to Sovereign Memory...")
        try:
            import dotenv
            # Load without touching os.environ yet
            values = dotenv.dotenv_values(env_path)
            
            # 1. Upsert / Update Present Keys
            for key, val in values.items():
                if val:
                    # Update DB (Source=env)
                    await self._update_db_config(key, val, "env")
                    # Update Runtime
                    os.environ[key] = str(val)
                    self._update_state_attributes(key, val)
            
            # 2. Prune Removed Keys (Ghost Config Fix)
            # Find all keys in DB that claim to be from "env" source
            try:
                # Use query parameter if possible, but execute_query interface here is raw string often.
                # Assuming safe simple query.
                q = "SELECT key FROM config_state WHERE source = 'env'"
                results = await run_query(self.state, q)
                
                if results:
                    db_keys = {item.get('key') for item in results if item.get('key')}
                    current_keys = set(values.keys())
                    
                    ghost_keys = db_keys - current_keys
                    
                    if ghost_keys:
                        logger.info(f"[Watcher] Pruning {len(ghost_keys)} ghost keys from Sovereign Memory: {ghost_keys}")
                        for ghost in ghost_keys:
                            # Delete from DB
                            # Note: DELETE returns [] usually
                            await run_query(self.state, f"DELETE FROM config_state WHERE key = '{ghost}';")
            except Exception as e:
                logger.warning(f"[Watcher] Failed to prune ghost keys (non-critical): {e}")
                    
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
                # Handle Nested 'system' block
                if key == "system" and isinstance(val, dict):
                    logger.info("[Watcher] Flattening 'system' block from config.yaml...")
                    for subkey, subval in val.items():
                        await self._update_db_config(subkey.upper(), subval, "config_yaml")
                        self._update_state_attributes(subkey.upper(), subval)
                    continue

                # Update DB (Source=config_yaml)
                await self._update_db_config(key.upper(), val, "config_yaml")
                # Update Runtime
                self._update_state_attributes(key.upper(), val)
                
            logger.info("[Watcher] config.yaml Sync Complete.")
        except Exception as e:
            logger.error(f"Failed to sync config.yaml: {e}")

    async def sync_mcp_from_disk(self):
        """
        Syncs mcp.yaml changes to Sovereign Memory (MCP Servers).
        When user edits file, file becomes source of truth → DB → Runtime.
        """
        mcp_path = self.state.agent_fs_root.parent / "config" / "mcp.yaml"
        if not mcp_path.exists(): 
            return

        logger.info("[Watcher] Syncing mcp.yaml to Sovereign Memory (user edit detected)...")
        try:
            with open(mcp_path, "r") as f:
                data = yaml.safe_load(f) or {}
                
            servers = data.get("mcp_servers", {})
            for name, config in servers.items():
                # Update DB (file is source of truth when user edits)
                await self.update_mcp_server(name, config)
            
            # [NEW] Reload runtime state (file edit → DB → Runtime)
            from agent_runner.config import load_mcp_servers
            await load_mcp_servers(self.state)
            
            # [NEW] Discover tools
            from agent_runner.service_registry import ServiceRegistry
            try:
                engine = ServiceRegistry.get_engine()
                await engine.discover_mcp_tools()
                logger.info("[Watcher] MCP tools reloaded after mcp.yaml change (user edit)")
            except RuntimeError:
                logger.warning("[Watcher] Could not reload MCP tools (engine not available)")
                
            logger.info(f"[Watcher] mcp.yaml Sync Complete ({len(servers)} servers updated, runtime reloaded).")
        except Exception as e:
            logger.error(f"Failed to sync mcp.yaml: {e}")

    async def sync_sovereign_from_disk(self):
        """Syncs sovereign.yaml changes to Sovereign Memory."""
        path = self.state.agent_fs_root.parent / "config" / "sovereign.yaml"
        if not path.exists(): return

        logger.info("[Watcher] Syncing sovereign.yaml to Sovereign Memory...")
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}

            # Sync Models (Rogue Six + others)
            # We map 'models' section to config keys
            if "models" in data:
                for k, v in data["models"].items():
                    # Map standard terms to Keys
                    # e.g. 'agent' -> 'AGENT_MODEL'
                    key_map = {
                        "agent": "AGENT_MODEL",
                        "router": "ROUTER_MODEL",
                        "healer": "HEALER_MODEL",
                        "summarizer": "SUMMARIZATION_MODEL",
                        "auditor": "AUDITOR_MODEL", # Not in State yet?
                        "cloud_vision": "VISION_MODEL",
                        "stt": "STT_MODEL"
                    }
                    db_key = key_map.get(k, k.upper() + "_MODEL")
                    await self._update_db_config(db_key, v, "sovereign_yaml")
                    self._update_state_attributes(db_key, v)

            # Sync Modes
            if "modes" in data:
                # Store the entire modes blob as a JSON string for easy retrieval
                import json
                blob = json.dumps(data["modes"])
                await self._update_db_config("MODES", blob, "sovereign_yaml")
                self._update_state_attributes("MODES", blob)
            
            # Sync Policies
            if "policies" in data:
                # We can store these individually or as a blob
                # For now, let's just log
                pass 

            logger.info("[Watcher] sovereign.yaml Sync Complete.")
        except Exception as e:
            logger.error(f"Failed to sync sovereign.yaml: {e}")
