"""
Complete Weather Task Implementation
Add this to agent_runner.py in _on_startup() before start_task_manager_delayed()
"""

# Weather update task using local Ollama model
async def weather_update_task() -> None:
    """Update weather file using local Ollama model with weather MCP server."""
    try:
        logger.info("Updating weather file with local Ollama model...")
        
        # Use local Ollama model (adjust to match your installed models)
        local_model = "ollama:mistral:latest"  # or "ollama:llama3.1:8b", "ollama:qwen2.5:7b", etc.
        
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
        weather_tools = []
        # Add weather MCP tools
        for tool in MCP_TOOLS:
            tool_name = tool.get("function", {}).get("name", "")
            if tool_name.startswith("mcp__weather__"):
                weather_tools.append(tool)
        # Add file writing tools
        for tool in FILE_TOOLS:
            tool_name = tool.get("function", {}).get("name", "")
            if tool_name in ["write_text", "make_dir"]:
                weather_tools.append(tool)
        
        # If no weather tools found, use all tools (fallback)
        if not weather_tools:
            weather_tools = None  # Will default to all tools
        
        # Call agent loop with local model
        result = await _agent_loop(
            user_messages=[{"role": "user", "content": weather_prompt}],
            model=local_model,  # Use local Ollama instead of AGENT_MODEL
            tools=weather_tools  # Only weather + file tools
        )
        
        logger.info("Weather file updated successfully using local Ollama model")
        
    except Exception as e:
        logger.error(f"Weather update task failed: {e}", exc_info=True)

# Register the task
task_manager.register(
    name="weather_update",
    func=weather_update_task,
    interval=300.0,  # 5 minutes = 300 seconds
    enabled=True,
    idle_only=False,  # Can run even when system is busy
    priority=TaskPriority.LOW,
    description="Update weather file using local Ollama model every 5 minutes",
    estimated_duration=10.0  # Local models might take a bit longer
)






