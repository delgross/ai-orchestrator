# Steps to Create Weather File That Updates Every 5 Minutes

## Quick Summary

1. **Add weather MCP server** to your config (or use HTTP API)
2. **Create the task function** that fetches weather and writes to file
3. **Register the task** with 5-minute interval
4. **Verify it works** via dashboard and file system

## Detailed Steps

### Step 1: Configure Weather Source

**Option A: Use Weather MCP Server**

Add to `agent_runner/agent_runner.env`:
```bash
# Add weather to your MCP_SERVERS list
MCP_SERVERS="...,weather=stdio:npx -y @modelcontextprotocol/server-weather"
```

**Option B: Use HTTP Weather API**

Add to `agent_runner/agent_runner.env`:
```bash
# Use HTTP weather service
MCP_SERVERS="...,weather=http://127.0.0.1:3000/mcp"
```

**Option C: Use Free Weather API (wttr.in)**

No MCP server needed - can use direct HTTP calls.

### Step 2: Add Task Function to agent_runner.py

Open `agent_runner/agent_runner.py` and find the `_on_startup()` function.

Add this code **before** the line `asyncio.create_task(start_task_manager_delayed())`:

```python
# Weather update task - updates weather file every 5 minutes
async def weather_update_task() -> None:
    """Update weather file in sandbox every 5 minutes."""
    try:
        logger.info("Updating weather file...")
        
        # Get weather data
        weather_info = None
        
        # Try MCP server first
        if "weather" in MCP_SERVERS:
            try:
                result = await tool_mcp_proxy(
                    server="weather",
                    tool="get_current_weather",
                    arguments={"location": "auto"}
                )
                if result.get("ok"):
                    weather_info = result.get("result", {})
            except Exception as e:
                logger.warning(f"Weather MCP failed: {e}")
        
        # Fallback to HTTP API if MCP not available
        if not weather_info and _http_client:
            try:
                resp = await _http_client.get("https://wttr.in/?format=j1", timeout=5.0)
                weather_info = resp.json()
            except Exception as e:
                logger.warning(f"Weather API failed: {e}")
        
        # Format weather data
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        weather_text = f"""Current Weather
================
Last Updated: {timestamp}

"""
        
        if isinstance(weather_info, dict):
            if "current_condition" in weather_info:
                # wttr.in format
                current = weather_info["current_condition"][0]
                weather_text += f"Temperature: {current.get('temp_F')}°F ({current.get('temp_C')}°C)\n"
                weather_text += f"Condition: {current.get('weatherDesc', [{}])[0].get('value', 'N/A')}\n"
                weather_text += f"Humidity: {current.get('humidity')}%\n"
                weather_text += f"Wind: {current.get('windspeedMiles')} mph\n"
            else:
                # Generic format
                import json
                weather_text += json.dumps(weather_info, indent=2)
        else:
            weather_text += str(weather_info) if weather_info else "Weather data unavailable"
        
        # Write to sandbox
        result = tool_write_text(
            path="weather/current_weather.txt",
            content=weather_text,
            overwrite=True
        )
        
        if result.get("ok"):
            logger.info(f"Weather file updated: weather/current_weather.txt")
        else:
            logger.error(f"Failed to write weather file: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Weather update task failed: {e}", exc_info=True)

# Register the task
task_manager.register(
    name="weather_update",
    func=weather_update_task,
    interval=300.0,  # 5 minutes
    enabled=True,
    idle_only=False,
    priority=TaskPriority.LOW,
    description="Update weather file in sandbox every 5 minutes",
    estimated_duration=5.0
)
```

### Step 3: Restart Agent Runner

```bash
cd /Users/bee/Sync/Antigravity/ai
./manage.sh restart
```

Or if running manually:
```bash
# Stop current instance (Ctrl+C or kill process)
# Then restart
cd agent_runner
source .venv/bin/activate
python3 -m uvicorn agent_runner:app --host 127.0.0.1 --port 5460
```

### Step 4: Verify It Works

1. **Check task is registered**:
   ```bash
   curl http://localhost:5460/admin/background-tasks | jq '.tasks.weather_update'
   ```

2. **Check scheduler dashboard**:
   - Open `http://localhost:5460/dashboard` (or router dashboard)
   - Go to "Idle Tasks" tab
   - Look for "weather_update" in the "Next Hour" column

3. **Check the file** (after 5 minutes):
   ```bash
   cat ~/ai/agent_fs_root/weather/current_weather.txt
   ```

4. **Check logs**:
   ```bash
   curl "http://localhost:5460/admin/dev/logs?limit=20&level=INFO" | grep weather
   ```

## Alternative: Use Agent Loop (Smarter)

If you want the AI agent to handle weather fetching intelligently:

```python
async def weather_update_task() -> None:
    """Update weather file using agent intelligence."""
    try:
        prompt = """Get the current weather for my location and write it to 
        weather/current_weather.txt in the sandbox. Format it nicely with:
        - Timestamp
        - Temperature (F and C)
        - Conditions
        - Humidity
        - Wind speed
        - Any relevant alerts or forecasts"""
        
        await _agent_loop([{"role": "user", "content": prompt}])
        logger.info("Weather file updated via agent")
    except Exception as e:
        logger.error(f"Weather update failed: {e}", exc_info=True)
```

This lets the agent figure out how to get weather (using available MCP servers or tools).

## Troubleshooting

- **Task not showing**: Check it's registered in `/admin/background-tasks`
- **File not created**: Check sandbox path `~/ai/agent_fs_root/weather/`
- **Weather data empty**: Verify MCP server is configured and working
- **Task not running**: Check if it's enabled and not blocked by dependencies

## File Location

The weather file will be created at:
```
~/ai/agent_fs_root/weather/current_weather.txt
```

You can read it via the agent using:
```
read_text(path="weather/current_weather.txt")
```






