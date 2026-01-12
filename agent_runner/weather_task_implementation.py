"""
Complete Weather Task Implementation
Add this to main.py or similar to register.
"""
import logging
import json
from typing import List, Dict, Any
from agent_runner.background_tasks import get_task_manager, TaskPriority

logger = logging.getLogger("weather_task")

async def weather_update_task() -> None:
    """Update weather file using local Ollama model with weather MCP server."""
    try:
        logger.info("Updating weather file with local Ollama model...")
        
        # Import here to avoid circular dependencies
        from agent_runner.agent_runner import (
            _agent_loop,
            MCP_TOOLS,
            FILE_TOOLS,
        )
        
        # Use local Ollama model
        local_model = "ollama:mistral:latest"
        
        # Create focused prompt for weather task
        weather_prompt = """Get the current weather using the weather MCP server tools and write it to 
weather/current_weather.txt in the sandbox. Include:
- Timestamp of when weather was fetched
- Temperature (both Fahrenheit and Celsius if available)
- Current conditions (sunny, cloudy, rain, etc.)
- Humidity percentage
- Wind speed and direction
- Any relevant weather alerts

Format it nicely and make it readable."""
        
        # Filter tools to only weather MCP + file writing tools (more efficient)
        weather_tools: List[Dict[str, Any]] = []
        # Add weather MCP tools
        for tool in MCP_TOOLS:
            tool_name = tool.get("function", {}).get("name", "")
            if tool_name.startswith("mcp__weather__") or tool_name == "mcp_proxy":
                weather_tools.append(tool)
        # Add file writing tools
        for tool in FILE_TOOLS:
            tool_name = tool.get("function", {}).get("name", "")
            if tool_name in ["write_text", "make_dir"]:
                weather_tools.append(tool)
        
        # Call agent loop
        await _agent_loop(
            messages=[{"role": "user", "content": weather_prompt}],
            model=local_model,
            tools=weather_tools if weather_tools else None
        )
        
        logger.info("Weather file updated successfully using local Ollama model")
        
    except Exception as e:
        logger.error(f"Weather update task failed: {e}", exc_info=True)

# Function to register the task
def register_weather_task() -> None:
    task_manager = get_task_manager()
    task_manager.register(
        name="weather_update",
        func=weather_update_task,
        interval=300.0,
        enabled=True,
        idle_only=False,
        priority=TaskPriority.LOW,
        description="Update weather file using local Ollama model every 5 minutes",
        estimated_duration=10.0
    )









