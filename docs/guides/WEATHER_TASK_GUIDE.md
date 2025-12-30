# Weather Update Task Guide

This guide explains how to set up a background task that updates a weather file in the sandbox every 5 minutes. It covers both using a standard MCP weather server and leveraging a local LLM (Ollama) for smarter formatting.

## Prerequisites

1.  **Weather MCP Server**: Ensure you have a weather server configured.
    -   **Option A (config.yaml)**:
        ```yaml
        mcp_servers:
          weather:
            type: stdio
            command: npx
            args: ["-y", "@modelcontextprotocol/server-weather"]
        ```
    -   **Option B (agent_runner.env)**:
        ```bash
        MCP_SERVERS="...,weather=stdio:npx -y @modelcontextprotocol/server-weather"
        ```

## Implementation

### 1. Define the Task Function
Add the following code to `agent_runner/engine.py` or as an extension. The logic below demonstrates the "Smart" approach using the agent's internal loop.

```python
async def weather_update_task(state: AgentEngine) -> None:
    """Update weather file using local Ollama model for intelligence."""
    try:
        # Use a local model for free, fast execution of utility tasks
        local_model = "ollama:mistral:latest" 
        
        prompt = """Get the current weather for my location and write it to 
        weather/current_weather.txt in the sandbox. Format it nicely with:
        - Timestamp, Temperature (F/C), and Conditions
        - Humidity and Wind Speed"""
        
        # Filter tools to just weather and file operations for efficiency
        weather_tools = [t for t in state.tool_definitions if "weather" in t['function']['name'] or "write_text" in t['function']['name']]
        
        await state._agent_loop(
            user_messages=[{"role": "user", "content": prompt}],
            model=local_model,
            tools=weather_tools
        )
        logger.info("Weather task completed successfully.")
    except Exception as e:
        logger.error(f"Weather update failed: {e}")
```

### 2. Register the Task
Register the task in the `AgentState` or `AgentEngine` initialization logic:

```python
task_manager.register(
    name="weather_update",
    func=weather_update_task,
    interval=300.0,  # 5 minutes
    priority=TaskPriority.LOW,
    description="Updates sandbox weather file every 5 mins"
)
```

## Verification

1.  **Dashboard**: Check the "Tasks" tab to see if `weather_update` is active.
2.  **Filesystem**: Verify that `agent_fs_root/weather/current_weather.txt` exists and updates periodically.
3.  **Logs**: Monitor for `Weather task completed successfully` entries.

## Troubleshooting
- **No data**: Ensure the weather MCP server is correctly initialized and has API access.
- **Model error**: Verify that the `local_model` specified (e.g., `mistral`) is available via `ollama list`.
- **Path error**: Ensure the `weather/` directory exists in your sandbox root or that the tool has permissions to create it.
