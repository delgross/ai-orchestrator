# Adaptable Task System - Add Any Periodic Task Easily

## Overview

The system is now **fully adaptable** for adding many types of periodic tasks (weather, time, stock quotes, etc.) without code changes. Just add configuration!

## Two Ways to Add Tasks

### Method 1: Configuration-Driven (Recommended) ✅

Add tasks to `config/config.yaml` - no code changes needed!

```yaml
agent_runner:
  periodic_tasks:
    weather_update:
      type: mcp_file
      mcp_server: weather
      prompt: "Get current weather and write to {output_file}"
      output_file: weather/current_weather.txt
      local_model: ollama:mistral:latest
      interval: 300.0  # 5 minutes
      priority: low
      enabled: true
    
    time_update:
      type: file
      prompt: "Get current time and write to {output_file}"
      output_file: time/current_time.txt
      local_model: ollama:mistral:latest
      interval: 60.0  # 1 minute
      priority: low
      enabled: true
    
    stock_quotes:
      type: mcp_file
      mcp_server: stocks  # When you add stocks MCP server
      prompt: "Get stock quotes for AAPL, MSFT, GOOGL and write to {output_file}"
      output_file: stocks/current_quotes.txt
      local_model: ollama:mistral:latest
      interval: 300.0  # 5 minutes
      priority: low
      enabled: true
```

### Method 2: Code-Based (For Complex Tasks)

Use the task factory in code:

```python
from agent_runner.task_factory import register_mcp_file_task

register_mcp_file_task(
    task_manager=task_manager,
    name="weather_update",
    mcp_server="weather",
    prompt="Get weather and write to {output_file}",
    output_file="weather/current.txt",
    local_model="ollama:mistral:latest",
    interval=300.0,
    priority=TaskPriority.LOW,
)
```

## Task Types

### 1. `mcp_file` - MCP Server + File
- Uses an MCP server to get data
- Writes result to a sandbox file
- Uses local Ollama model

**Example**: Weather, stock quotes, news, etc.

### 2. `file` - Simple File Task
- No MCP server needed
- Uses local Ollama for simple tasks
- Writes to file

**Example**: Time, date, system info, etc.

## Adding New Tasks - Step by Step

### Example: Add Stock Quotes Task

**Step 1**: Add stocks MCP server to `config/config.yaml`:
```yaml
mcp_servers:
  stocks:
    type: stdio
    command: npx
    args:
      - -y
      - '@your-stocks-mcp-server'  # Or whatever stocks MCP exists
```

**Step 2**: Add task to `config/config.yaml`:
```yaml
agent_runner:
  periodic_tasks:
    stock_quotes:
      type: mcp_file
      mcp_server: stocks
      prompt: |
        Get current stock quotes for AAPL, MSFT, GOOGL, TSLA and write to {output_file}.
        Include:
        - Stock symbol
        - Current price
        - Change (dollar and percent)
        - Volume
        - 52-week high/low
        - Timestamp
        Format as a readable table.
      output_file: stocks/current_quotes.txt
      local_model: ollama:mistral:latest
      interval: 300.0  # 5 minutes
      priority: low
      enabled: true
```

**Step 3**: Restart agent-runner
```bash
./manage.sh restart
```

**Done!** The task will automatically:
- Register itself
- Run every 5 minutes
- Use local Ollama model
- Call stocks MCP server
- Write to `stocks/current_quotes.txt`

### Example: Add Time Update Task

**Step 1**: Add to `config/config.yaml`:
```yaml
agent_runner:
  periodic_tasks:
    time_update:
      type: file  # No MCP server needed
      prompt: |
        Get the current date and time and write to {output_file}.
        Include:
        - Current date and time
        - Timezone
        - Day of week
        - Day of year
        - Week number
        Format it nicely.
      output_file: time/current_time.txt
      local_model: ollama:mistral:latest
      interval: 60.0  # 1 minute
      priority: low
      enabled: true
```

**Step 2**: Restart
```bash
./manage.sh restart
```

**Done!** Time file updates every minute.

## Task Configuration Options

```yaml
task_name:
  type: mcp_file | file          # Task type
  mcp_server: server_name        # MCP server (for mcp_file type)
  prompt: "Your prompt here"      # What the agent should do
  output_file: path/to/file.txt  # Where to write result
  local_model: ollama:mistral:latest  # Local model to use
  interval: 300.0                 # Update interval (seconds)
  priority: critical | high | medium | low | background
  enabled: true | false           # Enable/disable task
  idle_only: true | false         # Only run when idle
```

## Benefits

1. **No Code Changes**: Add tasks via config only
2. **Easy to Add**: Just copy/paste and modify
3. **Consistent**: All tasks use same pattern
4. **Efficient**: Uses local models (free, fast)
5. **Scalable**: Add as many tasks as you want

## Examples for Common Tasks

### Weather
```yaml
weather_update:
  type: mcp_file
  mcp_server: weather
  prompt: "Get current weather and write to {output_file}"
  output_file: weather/current.txt
  interval: 300.0
```

### Time
```yaml
time_update:
  type: file
  prompt: "Get current time and write to {output_file}"
  output_file: time/current.txt
  interval: 60.0
```

### Stock Quotes
```yaml
stock_quotes:
  type: mcp_file
  mcp_server: stocks
  prompt: "Get quotes for AAPL,MSFT,GOOGL and write to {output_file}"
  output_file: stocks/quotes.txt
  interval: 300.0
```

### News Headlines
```yaml
news_update:
  type: mcp_file
  mcp_server: news  # If you have a news MCP server
  prompt: "Get top news headlines and write to {output_file}"
  output_file: news/headlines.txt
  interval: 600.0  # 10 minutes
```

### System Stats
```yaml
system_stats:
  type: file
  prompt: "Get system stats (CPU, memory, disk) and write to {output_file}"
  output_file: system/stats.txt
  interval: 300.0
```

## How It Works

1. **Task Loader** reads `config/config.yaml` on startup
2. **Task Factory** creates task functions from config
3. **Task Manager** registers and schedules them
4. **Local Ollama** handles the reasoning
5. **MCP Servers** provide the data
6. **Files** are written to sandbox

## Future Enhancements

- Task templates library
- Task dependencies (run task B after task A)
- Conditional execution
- Task chaining
- Custom task types






