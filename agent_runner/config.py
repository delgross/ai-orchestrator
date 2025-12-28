import os
import json
import logging
import yaml
from pathlib import Path
from typing import Dict, Any
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner")

def load_mcp_servers(state: AgentState) -> None:
    """Load MCP servers from manifests and config."""
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
                        # Normalize 'command' + 'args' to 'cmd'
                        if "command" in cfg:
                            cmd = [cfg["command"]]
                            if "args" in cfg:
                                cmd.extend(cfg["args"])
                            cfg["cmd"] = cmd
                        state.mcp_servers[name] = cfg
        except Exception as e:
            logger.error(f"Failed to load config.yaml: {e}")

def load_agent_runner_limits(state: AgentState) -> None:
    """Load limits and general config from config.yaml."""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                cfg_data = yaml.safe_load(f)
                if cfg_data:
                    state.config = cfg_data
                    
                    # Update limits if present
                    if "agent_runner" in cfg_data and "limits" in cfg_data["agent_runner"]:
                        limits = cfg_data["agent_runner"]["limits"]
                        state.max_read_bytes = int(limits.get("max_read_bytes", state.max_read_bytes))
                        state.max_list_entries = int(limits.get("max_list_entries", state.max_list_entries))
                        state.max_tool_steps = int(limits.get("max_tool_steps", state.max_tool_steps))
        except Exception as e:
            logger.error(f"Failed to load config.yaml for limits: {e}")
