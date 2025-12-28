# Task Model Configuration

## Overview

The task system uses a **configurable model** for periodic background tasks. This model can be different from the main agent model, allowing you to:

- Use **local Ollama models** for tasks (fast, free)
- Run **multiple models simultaneously** (Ollama supports this)
- Keep **agent model** for main reasoning
- Use **task model** for background tasks

## Configuration

### In config.yaml

Add to `agent` section:

```yaml
agent:
  # ... other config ...
  tasks:
    model: ollama:mistral:latest  # Model for periodic background tasks
```

### Environment Variable

You can also set via environment variable:

```bash
export TASK_MODEL=ollama:mistral:latest
```

### Default

If not configured, defaults to: `ollama:mistral:latest`

## How It Works

### Multiple Models with Ollama

Ollama can run **multiple models simultaneously**. This means:

1. **Agent Model** (`AGENT_MODEL`) - Used for main agent reasoning
   - Example: `openai:gpt-5.2` or `ollama:qwq:latest`

2. **Task Model** (`TASK_MODEL`) - Used for periodic background tasks
   - Example: `ollama:mistral:latest`

3. **Summarization Model** - Used for text summarization
   - Example: `ollama:mistral:latest`

All three can be different models, and Ollama will handle them concurrently.

### Task-Specific Override

You can override the default task model per task:

```yaml
agent_runner:
  periodic_tasks:
    weather_update:
      type: mcp_file
      mcp_server: weather
      local_model: ollama:llama3.1:8b  # Override default task model
      output_file: weather/current.txt
      interval: 300.0
```

If `local_model` is not specified, it uses `TASK_MODEL` from config.

## Benefits

1. **Cost Efficiency**: Use free local models for tasks
2. **Performance**: Local models are fast for simple tasks
3. **Flexibility**: Different models for different purposes
4. **Scalability**: Ollama handles multiple models concurrently

## Health Check

The task server health check includes:
- Task model being used
- Number of enabled/running tasks
- Task manager status

View in dashboard: **System Health → Task Server**

## Examples

### Example 1: All Local Models

```yaml
agent:
  model: ollama:qwq:latest  # Main agent
  summarization:
    model: ollama:mistral:latest  # Summarization
  tasks:
    model: ollama:mistral:latest  # Background tasks
```

### Example 2: Mixed (Cloud + Local)

```yaml
agent:
  model: openai:gpt-5.2  # Main agent (cloud)
  summarization:
    model: ollama:mistral:latest  # Summarization (local)
  tasks:
    model: ollama:mistral:latest  # Tasks (local)
```

### Example 3: Task-Specific Models

```yaml
agent:
  tasks:
    model: ollama:mistral:latest  # Default for tasks

agent_runner:
  periodic_tasks:
    weather_update:
      local_model: ollama:mistral:latest  # Uses default
    complex_analysis:
      local_model: ollama:qwq:latest  # Override for this task
```

## Verification

Check current task model:

```bash
curl http://localhost:5460/admin/health | jq '.components.task_server.task_model'
```

Or view in dashboard: **System Health → Task Server**






