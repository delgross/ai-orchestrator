# Weather Task with Local Ollama Model

## Setup Steps

### Step 1: Add Weather MCP Server to config.yaml

Add this to `config/config.yaml` in the `mcp_servers` section:

```yaml
mcp_servers:
  weather:
    type: stdio
    command: npx
    args:
      - -y
      - '@modelcontextprotocol/server-weather'
```

### Step 2: Add Weather Task Function

Add this to `agent_runner/agent_runner.py` in the `_on_startup()` function, before `asyncio.create_task(start_task_manager_delayed())`:

```python
# Weather update task using local Ollama model
async def weather_update_task() -> None:
    """Update weather file using local Ollama model with weather MCP server."""
    try:
        logger.info("Updating weather file with local Ollama model...")
        
        # Use local Ollama model (adjust model name as needed)
        local_model = "ollama:mistral:latest"  # or "ollama:llama3.1:8b" or whatever you have
        
        # Create a focused prompt for weather
        weather_prompt = """Get the current weather using the weather MCP server tools and write it to 
weather/current_weather.txt in the sandbox. Include:
- Timestamp of when weather was fetched
- Temperature (both Fahrenheit and Celsius if available)
- Current conditions (sunny, cloudy, rain, etc.)
- Humidity percentage
- Wind speed and direction
- Any relevant weather alerts

Format it nicely and make it readable."""
        
        # Call agent loop with local model
        # Only provide weather MCP tools (not all tools) for efficiency
        weather_tools = [tool for tool in MCP_TOOLS if tool.get("function", {}).get("name", "").startswith("mcp__weather__")]
        weather_tools.extend([tool for tool in FILE_TOOLS if tool.get("function", {}).get("name") in ["write_text", "make_dir"]])
        
        result = await _agent_loop(
            user_messages=[{"role": "user", "content": weather_prompt}],
            model=local_model,  # Use local Ollama model instead of AGENT_MODEL
            tools=weather_tools  # Only weather MCP + file tools
        )
        
        logger.info("Weather file updated successfully using local model")
        
    except Exception as e:
        logger.error(f"Weather update task failed: {e}", exc_info=True)

# Register the task
task_manager.register(
    name="weather_update",
    func=weather_update_task,
    interval=300.0,  # 5 minutes = 300 seconds
    enabled=True,
    idle_only=False,  # Can run even when busy
    priority=TaskPriority.LOW,
    description="Update weather file using local Ollama model every 5 minutes",
    estimated_duration=10.0  # Local models might be a bit slower
)
```

### Step 3: Restart Agent Runner

```bash
./manage.sh restart
```

## How It Works

1. **Weather MCP Server**: Provides weather tools (like `get_current_weather`)
2. **Local Ollama Model**: Handles the reasoning and tool calling (fast, free, local)
3. **Agent Loop**: Uses the local model to:
   - Call weather MCP server tools
   - Get weather data
   - Format it nicely
   - Write to `weather/current_weather.txt`

## Benefits

- **Cost**: Free (local model, no API costs)
- **Speed**: Fast (local inference)
- **Privacy**: Weather data stays local
- **Reliability**: Works offline (once weather is fetched)

## Verify

1. Check task: `curl http://localhost:5460/admin/background-tasks | jq '.tasks.weather_update'`
2. Check file: `cat ~/ai/agent_fs_root/weather/current_weather.txt`
3. Check logs: `curl "http://localhost:5460/admin/dev/logs?level=INFO" | grep weather`

## Available Ollama Models

You can use any Ollama model you have installed:
- `ollama:mistral:latest`
- `ollama:llama3.1:8b`
- `ollama:qwen2.5:7b`
- etc.

Check what you have: `ollama list`






