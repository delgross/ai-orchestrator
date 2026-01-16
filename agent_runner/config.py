import json
import logging
import yaml
from pathlib import Path
from typing import Any, Dict
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query

logger = logging.getLogger("agent_runner")


def _normalize_cmd(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize legacy command/args format to cmd list."""
    if "command" in cfg:
        cmd = [cfg["command"]]
        if "args" in cfg:
            cmd.extend(cfg["args"])
        cfg["cmd"] = cmd
    return cfg


def _is_memory_available(state: "AgentState") -> bool:
    """Check if memory server is available and initialized."""
    return (hasattr(state, "memory") and
            state.memory is not None and
            getattr(state.memory, 'initialized', False))


async def _load_env_vars_from_db(state: "AgentState") -> Dict[str, str]:
    """Load environment variables from database for MCP server expansion."""
    db_env_vars = {}
    try:
        env_query = "SELECT key, value FROM config_state"
        env_results = await run_query(state, env_query)
        if env_results:
            for item in env_results:
                key = item.get("key")
                val = item.get("value")
                if key and val:
                    db_env_vars[key] = str(val)
                    # Ensure it's in os.environ for subprocess
                    if key not in os.environ:
                        os.environ[key] = str(val)
            if db_env_vars:
                logger.info(f"MCP: Loaded {len(db_env_vars)} env vars from database")
    except Exception as e:
        logger.warning(f"Failed to load env vars from database: {e}")
    return db_env_vars


def _expand_env_vars(value: Any, os_environ: Dict[str, str], db_env_vars: Dict[str, str]) -> Any:
    """Expand ${VAR} references in values using environment variables."""
    import re

    if isinstance(value, str):
        def replacer(m):
            var_name = m.group(1)
            # First check os.environ
            if var_name in os.environ:
                return os.environ[var_name]
            # Then check database cache
            elif var_name in db_env_vars:
                return db_env_vars[var_name]
            # Leave as-is if not found
            else:
                return m.group(0)

        return re.sub(r'\$\{([^}]+)\}', replacer, value)
    elif isinstance(value, list):
        return [_expand_env_vars(item, os_environ, db_env_vars) for item in value]
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v, os_environ, db_env_vars) for k, v in value.items()}
    else:
        return value


async def load_mcp_servers(state: AgentState) -> None:
    """Load MCP servers. Authority: Sovereign Memory (DB). Fallback: Disk."""
    # Helper to normalize legacy command/args to cmd
    def _normalize_cmd(cfg):
        if "command" in cfg:
            cmd = [cfg["command"]]
            if "args" in cfg:
                cmd.extend(cfg["args"])
            cfg["cmd"] = cmd
        return cfg

    # 1. Sovereign Boot (Check Database First)
    logger.info("MCP: Checking Sovereign Memory...")
    try:
        # [MEMORY ROBUSTNESS] Check memory server stability
        memory_available = _is_memory_available(state)
        memory_stable = not getattr(state, 'memory_unstable', False)

        # [FIX] Only clear if memory is available and stable - don't clear if memory is unstable
        # This prevents losing server configs when memory becomes unstable after initialization
        if memory_available and memory_stable:
            db_servers = await run_query(state, "SELECT * FROM mcp_server")
            if db_servers:
                logger.info(f"MCP: Loaded {len(db_servers)} servers from Sovereign Memory. IGNORING Disk Configs.")
                import os
                import re
                
                # Load ALL env vars from database for expansion (use ALL available resources)
                db_env_vars = {}
                try:
                    # Query ALL config_state entries (not just API keys) - use all available resources
                    env_query = "SELECT key, value FROM config_state"
                    env_results = await run_query(state, env_query)
                    if env_results:
                        for item in env_results:
                            key = item.get("key")
                            val = item.get("value")
                            if key and val:
                                db_env_vars[key] = str(val)
                                # Also ensure it's in os.environ for subprocess
                                if key not in os.environ:
                                    os.environ[key] = str(val)
                        if db_env_vars:
                            logger.info(f"MCP: Loaded {len(db_env_vars)} env vars from database for MCP server expansion")
                except Exception as e:
                    logger.warning(f"Failed to load env vars from database for MCP expansion: {e}")
                
                def expand_env_vars(value: Any) -> Any:
                    """Expand ${VAR} references in strings using os.environ and database cache."""
                    if isinstance(value, str):
                        def replacer(m):
                            var_name = m.group(1)
                            # First check os.environ (may have been set by _load_runtime_config_from_db)
                            if var_name in os.environ:
                                return os.environ[var_name]
                            # Then check database cache (loaded above)
                            if var_name in db_env_vars:
                                val = db_env_vars[var_name]
                                # Also set in os.environ for subprocess
                                os.environ[var_name] = val
                                return val
                            # Not found - return original so we can detect and report missing vars
                            return m.group(0)  # Return ${VAR} unchanged
                        return re.sub(r'\$\{([^}]+)\}', replacer, value)
                    return value
                
                missing_env_vars = []
                # [FIX] Build server configs in temporary dict first, only assign after successful load
                loaded_servers = {}
                for srv in db_servers:
                    name = srv["name"]
                    cmd = [srv.get("command", "")]
                    if srv.get("args"):
                        # Expand environment variables in args
                        expanded_args = []
                        for arg in srv.get("args", []):
                            expanded = expand_env_vars(arg)
                            expanded_args.append(expanded)
                            # Check if expansion failed (still contains ${VAR})
                            if isinstance(expanded, str) and "${" in expanded:
                                missing_vars = re.findall(r'\$\{([^}]+)\}', expanded)
                                for var in missing_vars:
                                    if not any(v["key"] == var and v["server"] == name for v in missing_env_vars):
                                        missing_env_vars.append({"server": name, "key": var, "location": "args"})
                        cmd.extend(expanded_args)
                    
                    # Expand environment variables in env dict values
                    env = srv.get("env", {})
                    expanded_env = {}
                    for k, v in env.items():
                        expanded = expand_env_vars(v)
                        expanded_env[k] = expanded
                        # Check if expansion failed
                        if isinstance(expanded, str) and "${" in expanded:
                            missing_vars = re.findall(r'\$\{([^}]+)\}', expanded)
                            for var in missing_vars:
                                if not any(v["key"] == var and v["server"] == name for v in missing_env_vars):
                                    missing_env_vars.append({"server": name, "key": var, "location": f"env.{k}"})
                    
                    # If env vars are missing but found in database, inject them into env dict
                    for missing in missing_env_vars:
                        if missing["server"] == name and missing["key"] in db_env_vars:
                            expanded_env[missing["key"]] = db_env_vars[missing["key"]]
                            logger.info(f"✅ Injected missing env var '{missing['key']}' from database into {name} server config")
                    
                    # Get enabled state and disabled_reason from database
                    db_enabled = srv.get("enabled", True)
                    db_disabled_reason = srv.get("disabled_reason")
                    
                    # Check circuit breaker state and disabled_reason
                    # This prevents re-enabling broken servers while respecting user intent in DB
                    final_enabled = db_enabled
                    if hasattr(state, "mcp_circuit_breaker"):
                        try:
                            cb = state.mcp_circuit_breaker.get_breaker(name)
                            cb_state = cb.state.value
                            
                            if cb_state == "open" or cb.permanently_disabled:
                                # Circuit breaker says server is broken - don't enable even if DB says enabled
                                final_enabled = False
                                if db_enabled:
                                    logger.debug(f"MCP: Server '{name}' enabled in DB but circuit breaker is OPEN - keeping disabled in runtime")
                            elif cb_state == "closed" and db_disabled_reason == "circuit_breaker_opened":
                                # [FIX] Do NOT auto-re-enable on boot. Trust the DB state.
                                # Circuit breakers are always closed on fresh boot (memory reset).
                                # Auto-re-enabling causes "zombie" servers to leak into context before failing again.
                                # Let admin tools or health checks explicitly re-enable it.
                                final_enabled = False 
                                logger.info(f"MCP: Server '{name}' disabled in DB (circuit breaker). Keeping disabled until explicit re-enable.")
                                
                                # Circuit breaker recovered but DB still says disabled - auto-re-enable
                                # final_enabled = True
                                # logger.info(f"MCP: Server '{name}' circuit breaker recovered - auto-re-enabling in runtime")
                                # # Update runtime state to clear disabled_reason
                                # if name in state.mcp_servers:
                                #     state.mcp_servers[name]["disabled_reason"] = None
                        except Exception as e:
                            logger.debug(f"MCP: Could not check circuit breaker for '{name}': {e}")
                            # If we can't check circuit breaker, trust DB value
                    
                    # Don't auto-re-enable if disabled_reason indicates user intent or permanent disable
                    if db_disabled_reason in ("user_disabled", "permanently_disabled", "intentionally_disabled"):
                        final_enabled = False
                        logger.debug(f"MCP: Server '{name}' has {db_disabled_reason} - preserving disabled state")
                    
                    cfg = {
                        "cmd": cmd,
                        "env": expanded_env,
                        "enabled": final_enabled,
                        "type": srv.get("type", "stdio")
                    }
                    loaded_servers[name] = cfg
                
                # Report missing env vars to user
                if missing_env_vars:
                    unique_missing = {}
                    for m in missing_env_vars:
                        key = m["key"]
                        if key not in unique_missing:
                            unique_missing[key] = []
                        unique_missing[key].append(f"{m['server']} ({m['location']})")
                    
                    for var_name, locations in unique_missing.items():
                        logger.warning(f"⚠️ Environment variable '{var_name}' not found in database. Required by: {', '.join(locations)}")
                        logger.warning(f"   💡 To fix: Store '{var_name}' in database via:")
                        logger.warning(f"      INSERT INTO config_state (key, value) VALUES ('{var_name}', 'your_value_here')")
                        logger.warning(f"   Or use: tool_set_env_var('{var_name}', 'your_value_here')")
                
                # Auto-inject ROUTER_AUTH_TOKEN into all MCP server environments
                # Get token from state (loaded from DB) or environment as fallback
                router_token = getattr(state, 'router_auth_token', None) or os.getenv('ROUTER_AUTH_TOKEN')
                if router_token:
                    for server_name, server_config in loaded_servers.items():
                        server_config.setdefault('env', {})
                        server_config['env']['ROUTER_AUTH_TOKEN'] = router_token
                        logger.debug(f"Auto-injected ROUTER_AUTH_TOKEN into MCP server '{server_name}'")

                # [FIX] Only clear and assign AFTER successfully loading from DB
                # This ensures we don't lose configs if DB load fails partway through
                state.mcp_servers.clear()
                state.mcp_servers.update(loaded_servers)
                logger.info(f"MCP: Successfully loaded {len(loaded_servers)} servers from database into runtime state")
                
                return # --- STOP HERE: DB IS TRUTH ---
    except Exception as e:
        logger.warning(f"Failed to load MCP servers from Sovereign DB: {e}")
        # [FIX] If memory is unavailable, fall back to disk config instead of preserving empty state
        if not (hasattr(state, "memory") and state.memory and state.memory.initialized):
            logger.warning("MCP: Memory unavailable - falling back to disk config")
            # Continue to disk loading instead of returning early
        else:
            # Memory is available but DB query failed - preserve existing configs if any
            logger.warning("MCP: Memory available but DB query failed - preserving existing server configs (if any)")
            # Don't clear - keep existing state.mcp_servers
            return

    # 2. Fallback: Disk Loading (ONLY if DB was confirmed empty)
    # Check if DB is actually empty before reading YAML
    disk_fallback_needed = False
    try:
        memory_available = _is_memory_available(state)
        memory_stable = not getattr(state, 'memory_unstable', False)

        if memory_available and memory_stable:
            count_result = await run_query(state, "SELECT count() FROM mcp_server GROUP ALL;")
            db_count = 0
            if count_result and len(count_result) > 0:
                db_count = count_result[0].get("count", 0)

            if db_count > 0:
                # DB has data, should not have reached here (early return should have caught it)
                logger.warning(f"MCP: DB has {db_count} servers but load failed. Preserving existing configs.")
                # [FIX] Don't clear - DB has data but query failed, preserve existing state
                return
        else:
            # Memory unavailable or unstable - force disk fallback
            disk_fallback_needed = True
            reason = "unavailable" if not memory_available else "unstable"
            logger.warning(f"MCP: Memory server {reason} - forcing disk fallback")

            # Increment appropriate counter
            counter_key = "disk_fallback_count" if not memory_available else "memory_instability_count"
            try:
                # Try to get current count
                counter_result = await run_query(state, "SELECT value FROM config_state WHERE key = 'disk_fallback_count'")
                current_count = 0
                if counter_result:
                    current_count = int(counter_result[0].get('value', '0'))

                # Increment counter
                new_count = current_count + 1
                await run_query(state, "UPDATE config_state SET value = $value WHERE key = 'disk_fallback_count'", {'value': str(new_count)})
                logger.info(f"MCP: Disk fallback count incremented to {new_count}")
            except Exception as e:
                logger.debug(f"MCP: Could not update disk fallback counter: {e}")

    except Exception as e:
        logger.debug(f"MCP: Could not check DB count: {e}")
        disk_fallback_needed = True

    # [FIX] Only clear if we're actually going to load from disk
    # This prevents clearing when memory is unavailable and we can't verify DB state
    if not state.mcp_servers:
        # Only clear if state is already empty (fresh start)
        state.mcp_servers.clear()
    
    # DB is confirmed empty - bootstrap from disk
    logger.info("MCP: Sovereign Memory Empty. Bootstrapping from Disk (one-time only)...")
    
    # 2a. Load from manifest files (preferred for code-deployment)
    manifest_dir = Path(__file__).parent.parent / "config" / "mcp_manifests"
    if manifest_dir.exists():
        for manifest_file in manifest_dir.glob("*.json"):
            try:
                with open(manifest_file, "r") as f:
                    data = json.load(f)
                    servers = data.get("mcpServers", data)
                    for name, cfg in servers.items():
                        # Normalize 'command' + 'args' to 'cmd'
                        if "command" in cfg:
                            cmd = [cfg["command"]]
                            if "args" in cfg:
                                cmd.extend(cfg["args"])
                            cfg["cmd"] = cmd

                        # Auto-inject ROUTER_AUTH_TOKEN
                        router_token = getattr(state, 'router_auth_token', None) or os.getenv('ROUTER_AUTH_TOKEN')
                        if router_token:
                            cfg.setdefault('env', {})
                            cfg['env']['ROUTER_AUTH_TOKEN'] = router_token
                            logger.debug(f"Auto-injected ROUTER_AUTH_TOKEN into MCP server '{name}' from manifest")

                        state.mcp_servers[name] = cfg
            except Exception as e:
                logger.error(f"Failed to load manifest {manifest_file}: {e}")

    # 2b. Load from dedicated mcp.yaml (if no manifests found)
    if not state.mcp_servers:
        mcp_config_path = Path(__file__).parent.parent / "config" / "mcp.yaml"
        if mcp_config_path.exists():
            try:
                with open(mcp_config_path, "r") as f:
                    mcp_data = yaml.safe_load(f)
                    if mcp_data and "mcp_servers" in mcp_data:
                        for name, cfg in mcp_data["mcp_servers"].items():
                            cfg = _normalize_cmd(cfg)

                            # Auto-inject ROUTER_AUTH_TOKEN
                            router_token = getattr(state, 'router_auth_token', None) or os.getenv('ROUTER_AUTH_TOKEN')
                            if router_token:
                                cfg.setdefault('env', {})
                                cfg['env']['ROUTER_AUTH_TOKEN'] = router_token
                                logger.debug(f"Auto-injected ROUTER_AUTH_TOKEN into MCP server '{name}' from mcp.yaml")

                            state.mcp_servers[name] = cfg
            except Exception as e:
                logger.error(f"Failed to load mcp.yaml: {e}")

    # 2c. Load from config.yaml (last resort, deprecated)
    if not state.mcp_servers:
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    cfg_data = yaml.safe_load(f)
                    if cfg_data and "mcp_servers" in cfg_data:
                        servers = cfg_data["mcp_servers"] or {}
                        for name, cfg in servers.items():
                            cfg = _normalize_cmd(cfg)

                            # Auto-inject ROUTER_AUTH_TOKEN
                            router_token = getattr(state, 'router_auth_token', None) or os.getenv('ROUTER_AUTH_TOKEN')
                            if router_token:
                                cfg.setdefault('env', {})
                                cfg['env']['ROUTER_AUTH_TOKEN'] = router_token
                                logger.debug(f"Auto-injected ROUTER_AUTH_TOKEN into MCP server '{name}' from config.yaml")

                            state.mcp_servers[name] = _normalize_cmd(cfg)
            except Exception as e:
                logger.error(f"Failed to load config.yaml: {e}")

    # 3. Bootstrap: Sync Disk -> DB (one-time only)
    if state.mcp_servers and hasattr(state, "config_manager"):
        logger.info("MCP: Bootstrapping Sovereign Memory from Disk (one-time sync)...")
        for name, cfg in state.mcp_servers.items():
            await state.config_manager.update_mcp_server(name, cfg)
        logger.info("MCP: Bootstrap complete. Database is now source of truth. YAML will not be read again.")

    # Note: Project Memory Sync removed for brevity in this method, 
    # it can be handled by a separate background task or startup hook if needed.


# Note: load_agent_runner_limits removed as its logic moved to AgentState._load_base_config()


