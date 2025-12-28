"""
Task Loader - Load and register tasks from configuration.

Allows defining periodic tasks in config.yaml without code changes.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

from agent_runner.task_factory import register_mcp_file_task, create_mcp_file_task
from agent_runner.background_tasks import TaskPriority

logger = logging.getLogger("agent_runner.task_loader")

# Default task model - can be overridden per task
try:
    from agent_runner.agent_runner import TASK_MODEL as DEFAULT_TASK_MODEL
except ImportError:
    DEFAULT_TASK_MODEL = "ollama:mistral:latest"


def load_tasks_from_config(config_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Load task definitions from config.yaml.
    
    Expected structure in config.yaml:
    ```yaml
    agent_runner:
      periodic_tasks:
        weather_update:
          type: mcp_file
          mcp_server: weather
          prompt: "Get weather and write to {output_file}"
          output_file: "weather/current.txt"
          local_model: "ollama:mistral:latest"
          interval: 300.0
          priority: low
          enabled: true
        time_update:
          type: file
          prompt: "Get current time and write to {output_file}"
          output_file: "time/current.txt"
          local_model: "ollama:mistral:latest"
          interval: 60.0
    ```
    """
    if yaml is None:
        logger.warning("yaml not available, cannot load tasks from config")
        return []
    
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    if not config_path.exists():
        logger.debug(f"Config file not found: {config_path}")
        return []
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
        
        agent_config = config.get("agent_runner", {})
        tasks_config = agent_config.get("periodic_tasks", {})
        
        if not tasks_config:
            return []
        
        tasks = []
        for task_name, task_config in tasks_config.items():
            if not isinstance(task_config, dict):
                continue
            
            task_type = task_config.get("type", "mcp_file")
            enabled = task_config.get("enabled", True)
            
            if not enabled:
                continue
            
            # Parse priority
            priority_str = task_config.get("priority", "low").upper()
            priority_map = {
                "CRITICAL": TaskPriority.CRITICAL,
                "HIGH": TaskPriority.HIGH,
                "MEDIUM": TaskPriority.MEDIUM,
                "LOW": TaskPriority.LOW,
                "BACKGROUND": TaskPriority.BACKGROUND,
            }
            priority = priority_map.get(priority_str, TaskPriority.LOW)
            
            task_def = {
                "name": task_name,
                "type": task_type,
                "enabled": enabled,
                "priority": priority,
                "config": task_config,
            }
            
            tasks.append(task_def)
        
        logger.info(f"Loaded {len(tasks)} periodic tasks from config")
        return tasks
        
    except Exception as e:
        logger.error(f"Failed to load tasks from config: {e}", exc_info=True)
        return []


def register_tasks_from_config(task_manager: Any, config_path: Optional[Path] = None) -> None:
    """
    Load tasks from config and register them with the task manager.
    """
    tasks = load_tasks_from_config(config_path)
    
    for task_def in tasks:
        try:
            name = task_def["name"]
            task_type = task_def["type"]
            task_config = task_def["config"]
            priority = task_def["priority"]
            
            if task_type == "mcp_file":
                # MCP server + file task
                mcp_server = task_config.get("mcp_server")
                if not mcp_server:
                    logger.warning(f"Task {name}: mcp_server not specified, skipping")
                    continue
                
                output_file = task_config.get("output_file", f"{name}.txt")
                prompt_template = task_config.get("prompt", f"Get data from {mcp_server} and write to {{output_file}}")
                prompt = prompt_template.format(output_file=output_file)
                
                register_mcp_file_task(
                    task_manager=task_manager,
                    name=name,
                    mcp_server=mcp_server,
                    prompt=prompt,
                    output_file=task_config.get("output_file", f"{name}.txt"),
                    local_model=task_config.get("local_model", DEFAULT_TASK_MODEL),
                    interval=float(task_config.get("interval", 300.0)),
                    priority=priority,
                    description=task_config.get("description", f"Update {name} from {mcp_server}"),
                    enabled=task_config.get("enabled", True),
                    idle_only=task_config.get("idle_only", False),
                )
                
            elif task_type == "file":
                # Simple file task (no MCP server)
                prompt = task_config.get("prompt", "").format(
                    output_file=task_config.get("output_file", f"{name}.txt")
                )
                
                # Create a simple file-writing task
                async def file_task_func():
                    from agent_runner.agent_runner import _agent_loop, FILE_TOOLS
                    await _agent_loop(
                        user_messages=[{"role": "user", "content": prompt}],
                        model=task_config.get("local_model", DEFAULT_TASK_MODEL),
                        tools=[t for t in FILE_TOOLS if t.get("function", {}).get("name") in ["write_text", "make_dir"]]
                    )
                
                file_task_func.__name__ = name
                
                task_manager.register(
                    name=name,
                    func=file_task_func,
                    interval=float(task_config.get("interval", 300.0)),
                    enabled=task_config.get("enabled", True),
                    idle_only=task_config.get("idle_only", False),
                    priority=priority,
                    description=task_config.get("description", f"Update {name} file"),
                    estimated_duration=5.0,
                )
            
            logger.info(f"Registered periodic task: {name} ({task_type})")
            
        except Exception as e:
            logger.error(f"Failed to register task {task_def.get('name', 'unknown')}: {e}", exc_info=True)

