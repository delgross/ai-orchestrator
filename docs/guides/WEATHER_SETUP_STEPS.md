# Weather File with Local Ollama Model - Complete Setup

## Overview
Create a weather file that updates every 5 minutes using:
- **Weather MCP Server** (provides weather tools)
- **Local Ollama Model** (handles reasoning - fast, free, local)
- **Background Task** (runs every 5 minutes)

## Step-by-Step Setup

### Step 1: Add Weather MCP Server ✅ (Already Done)
I've added the weather MCP server to `config/config.yaml`:
```yaml
weather:
  type: stdio
  command: npx
  args:
    - -y
    - '@modelcontextprotocol/server-weather'
```

### Step 2: Add Weather Task Function

Add this code to `agent_runner/agent_runner.py` in the `_on_startup()` function, 
**before** the line `asyncio.create_task(start_task_manager_delayed())`:

```python
# Weather update task using local Ollama model
async def weather_update_task() -> None:
    """Update weather file using local Ollama model with weather MCP server."""
    try:
        logger.info("Updating weather file with local Ollama model...")
        
        # Use local Ollama model (adjust to your installed models)
        local_model = "ollama:mistral:latest"  # Change to your preferred model
        
        weather_prompt = """Get the current weather using the weather MCP server tools and write it to 
weather/current_weather.txt in the sandbox. Include:
- Timestamp of when weather was fetched
- Temperature (both Fahrenheit and Celsius if available)
- Current conditions (sunny, cloudy, rain, etc.)
- Humidity percentage
- Wind speed and direction
- Any relevant weather alerts

Format it nicely and make it readable."""
        
        # Filter to only weather MCP + file tools (more efficient)
        weather_tools = []
        for tool in MCP_TOOLS:
            if tool.get("function", {}).get("name", "").startswith("mcp__weather__"):
                weather_tools.append(tool)
        for tool in FILE_TOOLS:
            if tool.get("function", {}).get("name") in ["write_text", "make_dir"]:
                weather_tools.append(tool)
        
        # Call agent loop with local model
        await _agent_loop(
            user_messages=[{"role": "user", "content": weather_prompt}],
            model=local_model,  # Use local Ollama instead of AGENT_MODEL
            tools=weather_tools if weather_tools else None
        )
        
        logger.info("Weather file updated successfully")
        
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
    description="Update weather file using local Ollama model every 5 minutes",
    estimated_duration=10.0
)
```

### Step 3: Choose Your Local Model

Check what Ollama models you have:
```bash
ollama list
```

Common options:
- `ollama:mistral:latest` - Fast, good for simple tasks
- `ollama:llama3.1:8b` - Balanced performance
- `ollama:qwen2.5:7b` - Good tool use
- `ollama:phi3:mini` - Very fast, lightweight

Update the `local_model` variable in the task function above.

### Step 4: Restart Agent Runner

```bash
cd /Users/bee/Sync/Antigravity/ai
./manage.sh restart
```

### Step 5: Verify It Works

1. **Check task is registered**:
   ```bash
   curl http://localhost:5460/admin/background-tasks | jq '.tasks.weather_update'
   ```

2. **Check scheduler**:
   - Dashboard → "Idle Tasks" tab
   - Should see "weather_update" in "Next Hour" column

3. **Wait 5 minutes** (or check immediately if it already ran)

4. **Check the file**:
   ```bash
   cat ~/ai/agent_fs_root/weather/current_weather.txt
   ```

5. **Check logs**:
   ```bash
   curl "http://localhost:5460/admin/dev/logs?limit=20&level=INFO" | grep weather
   ```

## How It Works

1. **Every 5 minutes**, the background task runs
2. **Local Ollama model** receives the prompt
3. **Ollama calls weather MCP server** tools (like `get_current_weather`)
4. **Weather data** is retrieved
5. **Ollama formats** the data nicely
6. **File is written** to `weather/current_weather.txt` in sandbox

## Benefits

- ✅ **Free**: No API costs (local model)
- ✅ **Fast**: Local inference is quick
- ✅ **Private**: Weather data stays local
- ✅ **Efficient**: Only uses weather + file tools
- ✅ **Reliable**: Works even if main agent is busy

## Troubleshooting

- **Task not running**: Check `/admin/background-tasks` to see if enabled
- **Weather MCP not found**: Restart agent-runner after adding to config.yaml
- **Model not found**: Check `ollama list` and update `local_model` variable
- **File not created**: Check sandbox path `~/ai/agent_fs_root/weather/`

## File Location

The weather file will be at:
```
~/ai/agent_fs_root/weather/current_weather.txt
```

You can read it via the agent or directly from the filesystem.






