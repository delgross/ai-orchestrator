import json
import logging
import yaml
from pathlib import Path
from typing import Dict, Any
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner")

async def load_mcp_servers(state: AgentState) -> None:
    """Load MCP servers from manifests and config and sync to memory."""
    state.mcp_servers.clear()
    
    # Helper to normalize legacy command/args to cmd
    def _normalize_cmd(cfg):
        if "command" in cfg:
            cmd = [cfg["command"]]
            if "args" in cfg:
                cmd.extend(cfg["args"])
            cfg["cmd"] = cmd
        return cfg
    
    # 1. Load from manifest files
    manifest_dir = Path(__file__).parent.parent / "config" / "mcp_manifests"
    if manifest_dir.exists():
        for manifest_file in manifest_dir.glob("*.json"):
            try:
                with open(manifest_file, "r") as f:
                    data = json.load(f)
                    servers = data.get("mcpServers", data)
                    for name, cfg in servers.items():
                        if name in state.mcp_servers:
                            logger.info(f"MCP: Updating existing server definition for '{name}' (from manifest {manifest_file.name})")
                        
                        # Normalize 'command' + 'args' to 'cmd'
                        if "command" in cfg:
                            cmd = [cfg["command"]]
                            if "args" in cfg:
                                cmd.extend(cfg["args"])
                            cfg["cmd"] = cmd
                        state.mcp_servers[name] = cfg
            except Exception as e:
                logger.error(f"Failed to load manifest {manifest_file}: {e}")

    # 2. Load from config.yaml
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                cfg_data = yaml.safe_load(f)
                if cfg_data and "mcp_servers" in cfg_data:
                    # Defensive: Handle case where mcp_servers is None (empty in yaml)
                    servers = cfg_data["mcp_servers"] or {}
                    for name, cfg in servers.items():
                        if name in state.mcp_servers:
                            logger.info(f"MCP: Updating/Overwriting server definition for '{name}' with config.yaml entry")
                        state.mcp_servers[name] = _normalize_cmd(cfg)
        except Exception as e:
            logger.error(f"Failed to load config.yaml: {e}")

    # 3. Load from dedicated mcp.yaml (Preferred)
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

    # 3. Auto-Sync to Project Memory
    # This ensures the database always has the latest server list for RAG/Tools
    
    # 3.5 Load from Sovereign Memory (DB) [Phase 51]
    try:
        if hasattr(state, "memory"):
            db_servers = await state.memory._execute_query("SELECT * FROM mcp_server")
            if db_servers:
                logger.info(f"MCP: Loaded {len(db_servers)} servers from Sovereign Memory.")
                for srv in db_servers:
                    name = srv["name"]
                    cmd = [srv.get("command", "")]
                    if srv.get("args"):
                        cmd.extend(srv["args"])
                    
                    cfg = {
                        "cmd": cmd,
                        "env": srv.get("env", {}),
                        "enabled": srv.get("enabled", True),
                        "type": srv.get("type", "stdio")
                    }
                    state.mcp_servers[name] = cfg
    except Exception as e:
        logger.warning(f"Failed to load MCP servers from Sovereign DB: {e}")

    if "project-memory" in state.mcp_servers:
        from agent_runner.tools.mcp import tool_mcp_proxy
        logger.info("Syncing MCP server definitions to Project Memory...")
        
        for name, cfg in state.mcp_servers.items():
            try:
                # Basic heuristic for github/info (can be improved later)
                github_url = "https://github.com/modelcontextprotocol/servers"
                if "args" in cfg:
                    # Try to find a package name in args
                    for arg in cfg.get("args", []):
                        if isinstance(arg, str) and arg.startswith("@") and "/" in arg:
                            github_url = f"https://www.npmjs.com/package/{arg}"
                            break
                            
                res = await tool_mcp_proxy(state, "project-memory", "store_mcp_intel", {
                    "name": name,
                    "github_url": github_url,
                    "newsletter": "Auto-Synced",
                    "similar_servers": []
                }, bypass_circuit_breaker=True)
                
                if not res.get("ok"):
                     print(f"DEBUG: Sync failed for {name}: {res.get('error')}")
                     logger.warning(f"Sync mcp intel failed for {name}: {res.get('error')}")
                else:
                     print(f"DEBUG: Sync success for {name}")

            except Exception as e:
                print(f"DEBUG: Sync Exception for {name}: {e}")
                logger.warning(f"Failed to sync MCP server '{name}' to memory: {e}")

        # 4. Prune old servers (Remove ones not in current config)
        try:
            active_servers = list(state.mcp_servers.keys())
            pres = await tool_mcp_proxy(state, "project-memory", "prune_offboarded_mcp_servers", {
                "active_servers": active_servers
            }, bypass_circuit_breaker=True)
            if pres.get("ok"):
                logger.info(f"Pruned offboarded MCP servers. Active: {len(active_servers)}")
            else:
                logger.warning(f"Failed to prune MCP servers: {pres.get('error')}")
        except Exception as e:
            logger.warning(f"Exception during MCP pruning: {e}")

# Note: load_agent_runner_limits removed as its logic moved to AgentState._load_base_config()


