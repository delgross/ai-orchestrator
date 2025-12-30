import json
import logging
import yaml
from pathlib import Path
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner")

async def load_mcp_servers(state: AgentState) -> None:
    """Load MCP servers from manifests and config and sync to memory."""
    state.mcp_servers.clear()
    
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
                    for name, cfg in cfg_data["mcp_servers"].items():
                        if name in state.mcp_servers:
                            logger.info(f"MCP: Updating/Overwriting server definition for '{name}' with config.yaml entry")
                            
                        # Normalize 'command' + 'args' to 'cmd'
                        if "command" in cfg:
                            cmd = [cfg["command"]]
                            if "args" in cfg:
                                cmd.extend(cfg["args"])
                            cfg["cmd"] = cmd
                        state.mcp_servers[name] = cfg
        except Exception as e:
            logger.error(f"Failed to load config.yaml: {e}")

    # 3. Auto-Sync to Project Memory
    # This ensures the database always has the latest server list for RAG/Tools
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

def load_agent_runner_limits(state: AgentState) -> None:
    """
    Load limits and general config from config.yaml.
    Note: Most logic moved to AgentState._load_base_config() for better priority handling.
    """
    pass

async def save_mcp_to_config(new_servers: Dict[str, Any]) -> bool:
    """Save/Merge new MCP servers into config.yaml."""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    if not config_path.exists():
        logger.error(f"config.yaml not found at {config_path}")
        return False
        
    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f) or {}
            
        if "mcp_servers" not in data:
            data["mcp_servers"] = {}
            
        # Merge
        for name, cfg in new_servers.items():
            data["mcp_servers"][name] = cfg
            
        with open(config_path, "w") as f:
            yaml.dump(data, f, sort_keys=False, indent=2)
            
        return True
    except Exception as e:
        logger.error(f"Failed to save MCP to config.yaml: {e}")
        return False
