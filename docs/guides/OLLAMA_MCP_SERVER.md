# Ollama MCP Server

## Overview

The Ollama MCP server provides programmatic access to Ollama model management through the Model Context Protocol. This allows the agent to manage its own models, download new ones, and adjust parameters dynamically.

## Features

### Available Tools

1. **`list_models`** - List all available Ollama models with details
   - Returns: Model names, sizes, digests, modification dates
   - Use case: Check what models are available

2. **`show_model`** - Show detailed information about a specific model
   - Parameters: `model` (e.g., "mistral:latest")
   - Returns: Model parameters, template, system prompt, details
   - Use case: Inspect model configuration

3. **`pull_model`** - Download/pull a model from Ollama library
   - Parameters: `model` (e.g., "llama3.2:3b"), `stream` (optional)
   - Returns: Download status
   - Use case: Install new models on demand

4. **`delete_model`** - Delete a model to free up disk space
   - Parameters: `model` (e.g., "mistral:latest")
   - Returns: Deletion status
   - Use case: Clean up unused models

5. **`copy_model`** - Copy a model to a new name
   - Parameters: `source`, `destination`
   - Returns: Copy status
   - Use case: Create model variants

6. **`generate_embeddings`** - Generate embeddings using an embedding model
   - Parameters: `model` (e.g., "embeddinggemma:300m"), `prompt`
   - Returns: Embedding vector and dimension
   - Use case: Generate embeddings for semantic search

7. **`generate_text`** - Generate text using /api/generate (non-chat)
   - Parameters: `model`, `prompt`, `options` (optional)
   - Returns: Generated text and token counts
   - Use case: Simple text generation without chat context

## Configuration

The server is configured in `config/config.yaml`:

```yaml
mcp_servers:
  ollama:
    type: stdio
    command: /Users/bee/Sync/Antigravity/ai/agent_runner/.venv/bin/python
    args:
    - /Users/bee/Sync/Antigravity/ai/agent_runner/ollama_server.py
    env:
      OLLAMA_BASE: http://127.0.0.1:11434
```

## Environment Variables

- `OLLAMA_BASE` - Ollama API base URL (default: `http://127.0.0.1:11434`)
- `OLLAMA_HTTP_TIMEOUT` - HTTP request timeout in seconds (default: `300.0`)

## Usage Examples

### List Available Models

```python
# Via agent tool call
result = await tool_mcp_proxy(
    server="ollama",
    tool="list_models",
    arguments={}
)
```

### Download a New Model

```python
result = await tool_mcp_proxy(
    server="ollama",
    tool="pull_model",
    arguments={"model": "llama3.2:3b"}
)
```

### Show Model Details

```python
result = await tool_mcp_proxy(
    server="ollama",
    tool="show_model",
    arguments={"model": "mistral:latest"}
)
```

### Generate Embeddings

```python
result = await tool_mcp_proxy(
    server="ollama",
    tool="generate_embeddings",
    arguments={
        "model": "embeddinggemma:300m",
        "prompt": "What is artificial intelligence?"
    }
)
```

### Delete Unused Model

```python
result = await tool_mcp_proxy(
    server="ollama",
    tool="delete_model",
    arguments={"model": "old-model:latest"}
)
```

## Benefits

1. **Self-Management**: Agent can manage its own models without manual intervention
2. **Dynamic Model Loading**: Download models on-demand based on task requirements
3. **Resource Optimization**: Delete unused models to free up disk space
4. **Parameter Inspection**: Check model details before use
5. **Embedding Generation**: Generate embeddings for semantic search/RAG

## Integration

The Ollama MCP server integrates seamlessly with:
- **Agent Runner**: Available as `mcp__ollama__*` tools
- **Task System**: Can be used in periodic tasks
- **Circuit Breaker**: Protected by MCP resilience system
- **Health Monitoring**: Included in health checks

## Security Considerations

- Only accessible locally (stdio transport)
- No authentication required (local Ollama instance)
- All operations are scoped to the local Ollama installation
- Model deletions are permanent - use with caution

## Error Handling

The server handles:
- Network errors (Ollama not running)
- Invalid model names
- API errors from Ollama
- Timeout errors
- JSON parsing errors

All errors are returned in a structured format:
```json
{
  "ok": false,
  "error": "Error message",
  "status_code": 404
}
```

## Testing

Test the server manually:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | \
  python agent_runner/ollama_server.py
```

## Future Enhancements

Potential additions:
- Model parameter modification
- Model quantization
- Batch operations
- Model performance metrics
- Streaming support for pull operations



