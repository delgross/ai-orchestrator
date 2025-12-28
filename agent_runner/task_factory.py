"""
Task Factory - Create reusable background tasks easily.

This makes it easy to create periodic tasks that:
- Use local Ollama models for simple tasks
- Call MCP servers
- Write results to sandbox files
- Run on configurable schedules
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional
from agent_runner.background_tasks import TaskPriority

logger = logging.getLogger("agent_runner.task_factory")


async def create_mcp_file_task(
    name: str,
    mcp_server: str,
    prompt: str,
    output_file: str,
    local_model: str = "ollama:mistral:latest",
    interval: float = 300.0,
    priority: TaskPriority = TaskPriority.LOW,
    description: str = "",
    enabled: bool = True,
    idle_only: bool = False,
) -> Callable:
    """
    Create a reusable task that:
    1. Uses a local Ollama model
    2. Calls an MCP server
    3. Writes result to a sandbox file
    
    Args:
        name: Task name (e.g., "weather_update")
        mcp_server: MCP server name (e.g., "weather")
        prompt: Prompt for the agent
        output_file: File path in sandbox (e.g., "weather/current.txt")
        local_model: Ollama model to use (e.g., "ollama:mistral:latest")
        interval: Update interval in seconds
        priority: Task priority
        description: Task description
        enabled: Whether task is enabled
        idle_only: Only run when idle
    
    Returns:
        Async function that can be registered as a task
    """
    async def task_function() -> None:
        """Generated task function."""
        try:
            logger.info(f"Running {name} task...")
            
            # Import here to avoid circular dependencies
            from agent_runner.agent_runner import (
                _agent_loop,
                MCP_TOOLS,
                FILE_TOOLS,
            )
            
            # Filter tools to only relevant MCP + file tools
            relevant_tools = []
            
            # Add MCP tools for this server
            for tool in MCP_TOOLS:
                tool_name = tool.get("function", {}).get("name", "")
                if tool_name.startswith(f"mcp__{mcp_server}__"):
                    relevant_tools.append(tool)
            
            # Add file writing tools
            for tool in FILE_TOOLS:
                tool_name = tool.get("function", {}).get("name", "")
                if tool_name in ["write_text", "make_dir", "read_text"]:
                    relevant_tools.append(tool)
            
            # If no MCP tools found, use all tools (fallback)
            if not any(t.get("function", {}).get("name", "").startswith(f"mcp__{mcp_server}__") for t in relevant_tools):
                logger.warning(f"No tools found for MCP server '{mcp_server}', using all tools")
                relevant_tools = None
            
            # Call agent loop with local model
            await _agent_loop(
                user_messages=[{"role": "user", "content": prompt}],
                model=local_model,
                tools=relevant_tools
            )
            
            logger.info(f"{name} task completed successfully")
            
        except Exception as e:
            logger.error(f"{name} task failed: {e}", exc_info=True)
    
    # Set function name for debugging
    task_function.__name__ = name
    
    return task_function


def register_mcp_file_task(
    task_manager: Any,
    name: str,
    mcp_server: str,
    prompt: str,
    output_file: str,
    local_model: str = "ollama:mistral:latest",
    interval: float = 300.0,
    priority: TaskPriority = TaskPriority.LOW,
    description: Optional[str] = None,
    enabled: bool = True,
    idle_only: bool = False,
) -> None:
    """
    Create and register a task in one call.
    
    This is a convenience function that creates the task and registers it.
    """
    task_func = create_mcp_file_task(
        name=name,
        mcp_server=mcp_server,
        prompt=prompt,
        output_file=output_file,
        local_model=local_model,
        interval=interval,
        priority=priority,
        description=description or f"Update {output_file} using {mcp_server} MCP server",
        enabled=enabled,
        idle_only=idle_only,
    )
    
    task_manager.register(
        name=name,
        func=task_func,
        interval=interval,
        enabled=enabled,
        idle_only=idle_only,
        priority=priority,
        description=description or f"Update {output_file} using {mcp_server} MCP server",
        estimated_duration=10.0,
    )


# Pre-defined task templates
TASK_TEMPLATES = {
    "weather": {
        "mcp_server": "weather",
        "prompt": """Get the current weather using the weather MCP server tools and write it to 
{output_file} in the sandbox. Include:
- Timestamp of when weather was fetched
- Temperature (both Fahrenheit and Celsius if available)
- Current conditions (sunny, cloudy, rain, etc.)
- Humidity percentage
- Wind speed and direction
- Any relevant weather alerts

Format it nicely and make it readable.""",
        "output_file": "weather/current_weather.txt",
        "interval": 300.0,  # 5 minutes
    },
    "time": {
        "mcp_server": None,  # No MCP needed - can use system time
        "prompt": """Get the current date and time and write it to {output_file} in the sandbox.
Include:
- Current date and time
- Timezone
- Day of week
- Day of year
- Week number
- Any relevant time-related information

Format it nicely.""",
        "output_file": "time/current_time.txt",
        "interval": 60.0,  # 1 minute
    },
    "stock_quotes": {
        "mcp_server": "stocks",  # Would need a stocks MCP server
        "prompt": """Get current stock quotes using the stocks MCP server and write to {output_file}.
Include:
- Stock symbols requested
- Current price
- Change (dollar and percent)
- Volume
- Market cap if available
- 52-week high/low
- Timestamp

Format as a readable table.""",
        "output_file": "stocks/current_quotes.txt",
        "interval": 300.0,  # 5 minutes
    },
}

