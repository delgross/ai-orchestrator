import json
import logging
import yaml
from pathlib import Path
from typing import Dict, Any
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner")

async def load_mcp_servers(state: AgentState) -> None:
    """Load MCP servers. Authority: Sovereign Memory (DB). Fallback: Disk."""
    state.mcp_servers.clear()
    
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
        if hasattr(state, "memory"):
            db_servers = await state.memory._execute_query("SELECT * FROM mcp_server")
            if db_servers:
                logger.info(f"MCP: Loaded {len(db_servers)} servers from Sovereign Memory. IGNORING Disk Configs.")
                for srv in db_servers:
                    name = srv["name"]
                    cmd = [srv.get("command", "")]
                    if srv.get("args"):
                        cmd.extend(srv.get("args", []))
                    
                    cfg = {
                        "cmd": cmd,
                        "env": srv.get("env", {}),
                        "enabled": srv.get("enabled", True),
                        "type": srv.get("type", "stdio")
                    }
                    state.mcp_servers[name] = cfg
                return # --- STOP HERE: DB IS TRUTH ---
    except Exception as e:
        logger.warning(f"Failed to load MCP servers from Sovereign DB: {e}")

    # 2. Fallback: Disk Loading (Only if DB was empty/failed)
    logger.info("MCP: Sovereign Memory Empty. Loading from Disk...")
    
    # 2a. Load from manifest files
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
                        state.mcp_servers[name] = cfg
            except Exception as e:
                logger.error(f"Failed to load manifest {manifest_file}: {e}")

    # 2b. Load from config.yaml
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                cfg_data = yaml.safe_load(f)
                if cfg_data and "mcp_servers" in cfg_data:
                    servers = cfg_data["mcp_servers"] or {}
                    for name, cfg in servers.items():
                        state.mcp_servers[name] = _normalize_cmd(cfg)
        except Exception as e:
            logger.error(f"Failed to load config.yaml: {e}")

    # 2c. Load from dedicated mcp.yaml (Preferred Disk Source)
    mcp_config_path = Path(__file__).parent.parent / "config" / "mcp.yaml"
    if mcp_config_path.exists():
        try:
            with open(mcp_config_path, "r") as f:
                mcp_data = yaml.safe_load(f)
                if mcp_data and "mcp_servers" in mcp_data:
                    for name, cfg in mcp_data["mcp_servers"].items():
                         state.mcp_servers[name] = _normalize_cmd(cfg)
        except Exception as e:
            logger.error(f"Failed to load mcp.yaml: {e}")

    # 3. Bootstrap: Sync Disk -> DB
    if state.mcp_servers and hasattr(state, "config_manager"):
        logger.info("MCP: Bootstrapping Sovereign Memory from Disk...")
        for name, cfg in state.mcp_servers.items():
            await state.config_manager.update_mcp_server(name, cfg)

    # Note: Project Memory Sync removed for brevity in this method, 
    # it can be handled by a separate background task or startup hook if needed.


# Note: load_agent_runner_limits removed as its logic moved to AgentState._load_base_config()


