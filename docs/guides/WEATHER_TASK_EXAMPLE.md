# Weather File Update Task - Step by Step

## Overview
Create a file in the sandbox that contains current weather information and updates every 5 minutes.

## Steps

### Step 1: Add Weather MCP Server (if not already configured)

Add a weather MCP server to `agent_runner/agent_runner.env`:

```bash
# Add to MCP_SERVERS (comma-separated)
MCP_SERVERS="...,weather=stdio:npx -y @modelcontextprotocol/server-weather"
```

Or use an HTTP weather API:
```bash
MCP_SERVERS="...,weather=http://127.0.0.1:3000/mcp"
```

### Step 2: Create the Weather Update Task Function

Add this function in `agent_runner/agent_runner.py` in the `_on_startup()` function, before the task manager starts:

```python
async def weather_update_task() -> None:
    """Update weather file in sandbox every 5 minutes."""
    try:
        logger.info("Updating weather file...")
        
        # Step 1: Get weather data from MCP server
        # Option A: Use MCP proxy if weather server is configured
        weather_data = None
        if "weather" in MCP_SERVERS:
            try:
                # Call weather MCP server (adjust tool name based on your weather server)
                result = await tool_mcp_proxy(
                    server="weather",
                    tool="get_weather",  # Adjust tool name as needed
                    arguments={"location": "current"}  # Adjust arguments as needed
                )
                
                if result.get("ok"):
                    weather_data = result.get("result", {})
                else:
                    logger.warning(f"Weather MCP call failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"Error calling weather MCP: {e}")
        
        # Option B: Use direct HTTP API if no MCP server
        if not weather_data and _http_client:
            try:
                # Example: OpenWeatherMap API (you'd need an API key)
                # resp = await _http_client.get(
                #     "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY"
                # )
                # weather_data = resp.json()
                pass
            except Exception as e:
                logger.error(f"Error calling weather API: {e}")
        
        if not weather_data:
            logger.warning("No weather data available, skipping update")
            return
        
        # Step 2: Format weather data as text
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format the weather information
        weather_text = f"""Current Weather Update
Last Updated: {timestamp}

"""
        
        # Add weather details (adjust based on your weather data structure)
        if isinstance(weather_data, dict):
            weather_text += f"Temperature: {weather_data.get('temperature', 'N/A')}\n"
            weather_text += f"Condition: {weather_data.get('condition', 'N/A')}\n"
            weather_text += f"Humidity: {weather_data.get('humidity', 'N/A')}\n"
            weather_text += f"Wind Speed: {weather_data.get('wind_speed', 'N/A')}\n"
        else:
            # If weather_data is a string or other format
            weather_text += f"{weather_data}\n"
        
        # Step 3: Write to sandbox file using the file tool
        file_path = "weather/current_weather.txt"
        result = tool_write_text(
            path=file_path,
            content=weather_text,
            overwrite=True  # Overwrite existing file
        )
        
        if result.get("ok"):
            logger.info(f"Weather file updated: {file_path}")
        else:
            logger.error(f"Failed to write weather file: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Weather update task failed: {e}", exc_info=True)
```

### Step 3: Register the Task

Add this registration in `_on_startup()`, after defining the function:

```python
# Register weather update task (runs every 5 minutes)
task_manager.register(
    name="weather_update",
    func=weather_update_task,
    interval=300.0,  # 5 minutes = 300 seconds
    enabled=True,
    idle_only=False,  # Run even if system is busy
    priority=TaskPriority.LOW,  # Low priority - won't block critical tasks
    description="Update weather file in sandbox every 5 minutes",
    estimated_duration=5.0  # Estimated 5 seconds to complete
)
```

### Step 4: Verify It Works

1. **Check task is registered**: Visit `http://localhost:5460/admin/background-tasks`
2. **Check scheduler**: Visit dashboard scheduler tab to see it in "Next Hour" column
3. **Check file**: After 5 minutes, check `~/ai/agent_fs_root/weather/current_weather.txt`
4. **Check logs**: View logs at `http://localhost:5460/admin/dev/logs?level=INFO`

## Complete Code Location

Add the code in `agent_runner/agent_runner.py` in the `_on_startup()` function, 
right before the line:
```python
asyncio.create_task(start_task_manager_delayed())
```

## Alternative: Use Agent Loop

If you want the agent to handle weather fetching intelligently:

```python
async def weather_update_task() -> None:
    """Update weather file using agent loop."""
    try:
        logger.info("Updating weather file via agent...")
        
        prompt = """Get the current weather and write it to weather/current_weather.txt in the sandbox.
        Format it nicely with timestamp, temperature, conditions, and other relevant details."""
        
        await _agent_loop([{"role": "user", "content": prompt}])
        logger.info("Weather file updated via agent")
    except Exception as e:
        logger.error(f"Weather update task failed: {e}", exc_info=True)
```

## Troubleshooting

1. **Task not running**: Check `/admin/background-tasks` to see if it's enabled
2. **MCP server not found**: Verify weather server is in `MCP_SERVERS` env var
3. **File not created**: Check sandbox permissions and path
4. **Weather data empty**: Check MCP server tool name and arguments






