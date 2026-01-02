"""
Task Loader - Load and register tasks from configuration.

Allows defining periodic tasks in config.yaml without code changes.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    import yaml # type: ignore[import-untyped]
except ImportError:
    yaml = None

from agent_runner.task_factory import register_mcp_file_task
from agent_runner.background_tasks import TaskPriority

logger = logging.getLogger("agent_runner.task_loader")

# Default task model - can be overridden per task
try:
    from agent_runner.agent_runner import TASK_MODEL as DEFAULT_TASK_MODEL
except ImportError:
    DEFAULT_TASK_MODEL = "ollama:mistral:latest"


def load_tasks_from_config(config_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Load task definitions from a configuration dictionary.
    """
    if not config_data:
        # Fallback to reading file if no data passed (legacy behavior but discouraged)
        if yaml is None:
            logger.warning("yaml not available, cannot load config file")
            return []
            
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        if not config_path.exists():
            return []
            
        try:
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            return []
    
    try:
        agent_config = config_data.get("agent_runner", {})
        # Flatten structure: config might carry periodic_tasks directly if it's the root config
        # But usually nested in agent_runner or user provided dict. 
        # State.config matches the file structure (root keys: agent_runner, router, etc.)
        
        # Check both root and nested just in case
        tasks_config = agent_config.get("periodic_tasks", config_data.get("periodic_tasks", {}))
        
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


async def load_tasks_from_db(state: Any) -> List[Dict[str, Any]]:
    """
    Load task definitions from Sovereign Memory (task_def table).
    """
    try:
        from agent_runner.memory_server import MemoryServer
        # We need a memory client. State should have one, or we make one.
        if not hasattr(state, "memory") or not state.memory:
            return []
            
        memory = state.memory
        
        # Query all tasks
        query = "SELECT * FROM task_def"
        results = await memory._execute_query(query)
        
        if not results:
            return []
            
        tasks = []
        for row in results:
            # Map DB fields to Task Definition format
            priority_str = str(row.get("priority", "low")).upper()
            priority_map = {
                "CRITICAL": TaskPriority.CRITICAL,
                "HIGH": TaskPriority.HIGH,
                "MEDIUM": TaskPriority.MEDIUM,
                "LOW": TaskPriority.LOW,
                "BACKGROUND": TaskPriority.BACKGROUND,
            }
            priority = priority_map.get(priority_str, TaskPriority.LOW)

            task_def = {
                "name": row.get("name"),
                "type": row.get("type", "agent"),
                "enabled": row.get("enabled", True),
                "priority": priority,
                # Reconstruct config dict
                "config": row.get("config", {}) or {}
            }
            
            # Ensure config has critical fields even if flattened in table
            if "prompt" in row: task_def["config"]["prompt"] = row["prompt"]
            if "description" in row: task_def["config"]["description"] = row["description"]
            if "schedule" in row: task_def["config"]["schedule"] = row["schedule"]
            if "idle_only" in row: task_def["config"]["idle_only"] = row["idle_only"]
            
            tasks.append(task_def)
            
        logger.info(f"Loaded {len(tasks)} periodic tasks from Sovereign Memory.")
        return tasks
        
    except Exception as e:
        logger.error(f"Failed to load tasks from DB: {e}")
        return []


async def register_tasks_from_config(task_manager: Any, config_data: Optional[Dict[str, Any]] = None, state: Any = None) -> None:
    """
    Load tasks from config dict AND Sovereign DB, then register them.
    """
    # 1. Load from Config (Legacy/Boot)
    tasks_cfg = load_tasks_from_config(config_data)
    
    # 2. Load from DB (Sovereign)
    tasks_db = []
    if state:
        tasks_db = await load_tasks_from_db(state)
        
    # 3. Merge (DB overrides Config)
    # Using dictionary by name to dedup
    merged = {t["name"]: t for t in tasks_cfg}
    for t in tasks_db:
        merged[t["name"]] = t
        
    tasks = list(merged.values())
    
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
                    min_tempo=task_config.get("min_tempo"), # [NEW]
                )
                
            elif task_type == "file":
                # Simple file task (no MCP server)
                prompt = task_config.get("prompt", "").format(
                    output_file=task_config.get("output_file", f"{name}.txt")
                )
                
                # Create a simple file-writing task
                async def file_task_func():
                    from agent_runner.agent_runner import _agent_loop
                    await _agent_loop(
                        user_messages=[{"role": "user", "content": prompt}],
                        model=task_config.get("local_model", DEFAULT_TASK_MODEL),
                        tools=None  # Use all available tools (ServiceRegistry)
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
                    min_tempo=task_config.get("min_tempo"), # [NEW]
                )
            
            elif task_type == "module":
                # [NEW] Direct Module Function Execution
                # Efficiently runs a specific Python function without Agent overhead.
                # Config: { "module": "agent_runner.mcp_tasks", "function": "mcp_refresh_task" }
                
                module_path = task_config.get("module")
                func_name = task_config.get("function")
                
                if not module_path or not func_name:
                    logger.warning(f"Task {name} (module) missing 'module' or 'function' path.")
                    continue
                    
                import importlib
                try:
                    mod = importlib.import_module(module_path)
                    task_func = getattr(mod, func_name)
                    
                    # Ensure it's a coroutine if needed, or wrap it
                    # The BackgroundTaskManager expects async functions
                    
                    schedule = task_config.get("schedule")
                    interval = task_config.get("interval")
                    if interval is not None:
                        interval = float(interval)
                    
                    task_manager.register(
                        name=name,
                        func=task_func,
                        interval=interval,
                        schedule=schedule,
                        enabled=task_config.get("enabled", True),
                        idle_only=task_config.get("idle_only", False),
                        priority=priority,
                        description=task_config.get("description", f"Module Task: {module_path}.{func_name}"),
                        estimated_duration=task_config.get("estimated_duration", 60.0),
                        min_tempo=task_config.get("min_tempo"), # [NEW]
                    )
                    logger.info(f"Registered module task: {name} -> {module_path}.{func_name}")
                    
                except ImportError as e:
                    logger.error(f"Failed to load module for task {name}: {e}")
                except AttributeError as e:
                    logger.error(f"Failed to find function for task {name}: {e}")

            elif task_type == "agent":
                # Generic Agent Task using internal tools
                # Allows specifying a list of tools to enable for this task
                
                # Extract known scheduling keys
                known_keys = {"tools", "prompt", "type", "enabled", "idle_only", 
                              "priority", "description", "estimated_duration", 
                              "interval", "schedule", "name"}
                
                # Check for schedule vs interval
                schedule = task_config.get("schedule")
                interval = task_config.get("interval")
                if interval is not None:
                    interval = float(interval)
                
                # Define the worker function
                async def agent_task_func():
                    from agent_runner.agent_runner import _agent_loop, get_shared_engine
                    
                    # Resolve tools
                    requested_tools = task_config.get("tools", [])
                    engine = get_shared_engine()
                    all_tools = await engine.get_all_tools()
                    
                    active_tools = []
                    if requested_tools == "all":
                        active_tools = all_tools
                    else:
                        # Filter by name
                        req_set = set(requested_tools)
                        active_tools = [
                            t for t in all_tools 
                            if t.get("function", {}).get("name") in req_set
                        ]
                    
                    prompt = task_config.get("prompt", f"Run task: {name}")
                    
                    result = await _agent_loop(
                        user_messages=[{"role": "user", "content": prompt}],
                        model=task_config.get("local_model", DEFAULT_TASK_MODEL),
                        tools=active_tools
                    )
                    
                    # CIRCUIT BREAKER: Check for logic failures that didn't raise exceptions
                    if isinstance(result, dict) and "error" in result:
                        raise RuntimeError(f"Agent failed to complete task: {result['error']}")
                    
                    # Check for empty choices (provider failure)
                    if isinstance(result, dict) and not result.get("choices") and not result.get("error"):
                         raise RuntimeError("Agent returned empty response (Provider Failure)")

                agent_task_func.__name__ = name
                
                task_manager.register(
                    name=name,
                    func=agent_task_func,
                    interval=interval,
                    schedule=schedule,
                    enabled=task_config.get("enabled", True),
                    idle_only=task_config.get("idle_only", False),
                    priority=priority,
                    description=task_config.get("description", f"Agent Task: {name}"),
                    estimated_duration=task_config.get("estimated_duration", 300.0),
                    min_tempo=task_config.get("min_tempo"), # [NEW]
                )

            logger.info(f"Registered periodic task: {name} ({task_type})")
            
        except Exception as e:
            logger.error(f"Failed to register task {task_def.get('name', 'unknown')}: {e}", exc_info=True)

