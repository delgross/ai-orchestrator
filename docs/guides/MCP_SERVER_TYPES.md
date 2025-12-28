# MCP Server Types - Local vs Remote

## Current Configuration

### Local MCP Servers (stdio) ✅
These run as **local processes** on your machine:

1. **firecrawl-mcp** - `type: stdio` - Web scraping
2. **mcp-pandoc** - `type: stdio` - Document conversion
3. **tavily-search** - `type: stdio` - Search (uses API key but runs locally)
4. **scrapezy** - `type: stdio` - Web scraping
5. **perplexity** - `type: stdio` - Search (uses API key but runs locally)
6. **thinking** - `type: stdio` - Sequential thinking
7. **project-memory** - `type: stdio` - Your local memory server
8. **playwright** - `type: stdio` - Browser automation
9. **macos_automator** - `type: stdio` - macOS automation
10. **weather** - `type: stdio` - Weather data (runs locally via npx)

### Remote MCP Servers (sse/http/ws) ⚠️
These connect to **remote servers**:

1. **exa** - `type: sse` - `url: https://mcp.exa.ai/mcp` - Remote search API

## Task System Behavior

### Does it rely on remote servers?

**No!** The task system works with **both local and remote** MCP servers, but:

1. **Local servers are preferred** for periodic tasks:
   - Faster (no network latency)
   - More reliable (no internet dependency)
   - Private (data stays local)
   - Free (no API costs for the server itself)

2. **Remote servers work too**, but:
   - Require internet connection
   - May have API rate limits
   - May incur costs
   - Slower due to network latency

### Weather Task Example

The weather task uses:
- **Local Ollama model** (runs on your machine)
- **Local weather MCP server** (runs via `npx` on your machine)
- **No remote dependencies** for the task execution itself

However, the weather MCP server itself may call remote APIs to get weather data (that's how it works - the server is local but fetches data from weather APIs).

## Adding More Local MCP Servers

You can add any MCP server that runs locally:

```yaml
mcp_servers:
  my_local_server:
    type: stdio
    command: npx  # or python, node, etc.
    args:
      - -y
      - '@package/name'
    env: {}
```

## Task Configuration

When creating tasks, you can use **any MCP server** (local or remote):

```yaml
agent_runner:
  periodic_tasks:
    weather_update:
      type: mcp_file
      mcp_server: weather  # Local stdio server ✅
      # ... rest of config
    
    search_update:
      type: mcp_file
      mcp_server: exa  # Remote sse server ⚠️ (requires internet)
      # ... rest of config
```

## Recommendations

For periodic tasks, prefer:
1. **Local stdio MCP servers** - Best for reliability
2. **Local Ollama models** - Fast and free
3. **Simple file tasks** - No external dependencies

Avoid for periodic tasks:
- Remote MCP servers (unless necessary)
- Expensive API calls
- Tasks that require internet (unless that's the point)

## Summary

- ✅ **Task system does NOT require remote MCP servers**
- ✅ **Most MCP servers are local (stdio)**
- ✅ **Weather task uses local MCP server**
- ⚠️ **One remote server (exa) exists but isn't required for tasks**
- ✅ **You can add more local MCP servers easily**






