# Remote MCP Servers in Tasks

## Yes, Future Tasks Can Use Remote MCP Servers! ✅

The task system **already supports** remote MCP servers. The task factory doesn't distinguish between local and remote - it just uses the MCP server name you specify.

## How It Works

### Current Support

The system supports these MCP server types:

1. **stdio** - Local process (most common)
2. **sse** - Server-Sent Events (remote)
3. **http** - HTTP endpoint (remote)
4. **ws** - WebSocket (remote)
5. **unix** - Unix socket (local)

### Example: Remote MCP Server

You already have one remote server configured:

```yaml
mcp_servers:
  exa:
    type: sse
    url: https://mcp.exa.ai/mcp
    query_params:
      exaApiKey: your-key-here
```

### Using Remote MCP in Tasks

You can use **any MCP server** (local or remote) in tasks:

```yaml
agent_runner:
  periodic_tasks:
    # Local MCP server (stdio)
    weather_update:
      type: mcp_file
      mcp_server: weather  # Local stdio server
      output_file: weather/current.txt
      interval: 300.0
    
    # Remote MCP server (sse/http/ws)
    search_update:
      type: mcp_file
      mcp_server: exa  # Remote sse server
      prompt: "Search for latest AI news and write to {output_file}"
      output_file: news/ai_news.txt
      interval: 600.0
      priority: low
      enabled: true
```

The task factory doesn't care - it just looks up the MCP server by name and uses whatever tools it provides.

## Adding Remote MCP Servers

### Example 1: HTTP MCP Server

```yaml
mcp_servers:
  my_remote_api:
    type: http
    url: https://api.example.com/mcp
    # Optional: Add auth token via env var MCP_TOKEN_MY_REMOTE_API
```

### Example 2: WebSocket MCP Server

```yaml
mcp_servers:
  realtime_data:
    type: ws
    url: wss://realtime.example.com/mcp
    # Optional: Add auth token via env var MCP_TOKEN_REALTIME_DATA
```

### Example 3: SSE MCP Server (like exa)

```yaml
mcp_servers:
  another_remote:
    type: sse
    url: https://remote.example.com/mcp
    query_params:
      apiKey: your-key
```

## Task Configuration - No Difference

When creating tasks, you specify the MCP server name - the system handles local vs remote automatically:

```yaml
agent_runner:
  periodic_tasks:
    # Works with local servers
    weather_update:
      mcp_server: weather  # stdio - local
    
    # Works with remote servers
    remote_data_update:
      mcp_server: my_remote_api  # http - remote
    
    # Works with any type
    mixed_task:
      mcp_server: exa  # sse - remote
```

## Trade-offs: Local vs Remote

### Local MCP Servers (stdio)
✅ Faster (no network latency)  
✅ More reliable (no internet dependency)  
✅ Private (data stays local)  
✅ Free (no API costs for server process)  
❌ May still call remote APIs (like weather APIs)

### Remote MCP Servers (http/sse/ws)
✅ Access to cloud services  
✅ No local installation needed  
✅ Can leverage powerful remote infrastructure  
❌ Requires internet connection  
❌ Network latency  
❌ May have API rate limits/costs  
❌ Less reliable (network issues)

## Best Practices

### For Periodic Tasks

1. **Prefer local servers** when possible:
   - Weather, time, system stats
   - Tasks that run frequently

2. **Use remote servers** when needed:
   - Cloud-only services
   - Services that require remote infrastructure
   - Tasks that can tolerate network issues

3. **Consider hybrid approaches**:
   - Use local Ollama model (fast, free)
   - Call remote MCP server (when needed)
   - Cache results locally

### Example: Hybrid Task

```yaml
agent_runner:
  periodic_tasks:
    cloud_data_sync:
      type: mcp_file
      mcp_server: cloud_api  # Remote server
      prompt: "Fetch latest data from cloud API and write to {output_file}"
      output_file: data/cloud_sync.txt
      local_model: ollama:mistral:latest  # Local model, remote data
      interval: 3600.0  # 1 hour (less frequent due to remote dependency)
      priority: medium
      enabled: true
```

## Future-Proof Design

The system is designed to handle:

1. **Any MCP server type** - stdio, http, sse, ws, unix
2. **Mixed environments** - Local and remote servers together
3. **Dynamic configuration** - Add servers without code changes
4. **Flexible tasks** - Use any server in any task

## Summary

✅ **Yes, future tasks can use remote MCP servers**  
✅ **System already supports remote servers**  
✅ **No code changes needed - just config**  
✅ **Task factory works with both local and remote**  
✅ **You can mix local and remote servers in tasks**

The task system is **fully flexible** - use whatever MCP servers (local or remote) make sense for each task!






