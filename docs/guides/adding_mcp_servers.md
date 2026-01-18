# Adding MCP Servers

## Quick Start

To add an MCP server, you have **four options**:

1. **Upload a config file** via API - LLM analyzes and reformats it automatically (easiest!)
2. **Drop a JSON manifest file** in `config/mcp_manifests/` (auto-scanned)
3. **Edit `config/config.yaml`** and add to `mcp_servers:` section
4. **Set environment variable** `MCP_SERVERS` (legacy)

Then reload the servers (no restart needed).

## Configuration Methods

### Method 1: Upload Config File (Easiest - LLM-Powered) ✅

**Upload any text file with MCP server configuration and let the LLM analyze and reformat it!**

The system will:
- Analyze the file (supports JSON, YAML, plain text, Claude Desktop format)
- Extract all MCP server definitions
- Reformat to match our YAML format
- Merge into `config.yaml`
- Automatically reload MCP servers

**Usage:**
```bash
curl -X POST http://127.0.0.1:5460/admin/mcp/upload-config \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@mcp-servers.txt"
```

**Supported formats:**
- Claude Desktop JSON: `{"mcpServers": {"server": {"command": "npx", "args": ["package"]}}}`
- YAML format
- Plain text descriptions
- Multiple servers in one file

**Response (success):**
```json
{
  "ok": true,
  "message": "Successfully processed 3 server(s)",
  "added": ["server1", "server2"],
  "updated": ["server3"],
  "skipped": [],
  "warnings": ["Server 'server1': Same command as 'server2' in upload"],
  "total_servers": 15
}
```

**Response (validation errors):**
```json
{
  "ok": false,
  "error": "Validation failed",
  "validation_errors": [
    "Server 'bad-server': stdio servers require 'command' field",
    "Server 'bad-url': http URL must start with http:// or https://"
  ],
  "warnings": ["Server 'duplicate': Same URL as 'existing' in upload"]
}
```

**Features:**
- ✅ **Validates** server configurations (required fields, URL formats, etc.)
- ✅ **Checks for redundancy** (duplicate names, same commands/URLs)
- ✅ **Warns** about potential issues without blocking
- ✅ **Blocks** invalid configurations with clear error messages

**Note:** Requires authentication token (same as other `/admin` endpoints).

### Method 2: JSON Manifest Files (Auto-scanned) ✅

**Just drop a `.json` file in `config/mcp_manifests/`** and the system will automatically scan and load it!

**Claude Desktop Format:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@package/name"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

**Multiple servers in one file** (separated by `+` or blank lines):
```json
{"mcpServers": {"server1": {"command": "npx", "args": ["package1"]}}}
+
{"mcpServers": {"server2": {"command": "npx", "args": ["package2"]}}}
```

**After adding:**
- Servers are automatically loaded on next reload (every 6 hours)
- Or manually reload: `curl -X POST http://127.0.0.1:5460/admin/reload-mcp`

**Priority:** Manifest files are loaded first, then `config.yaml` (which can override manifests).

### Method 2: YAML Configuration (Recommended for complex configs) ✅

Edit `config/config.yaml`:

```yaml
mcp_servers:
  your-server-name:
    type: stdio  # or http, sse, ws, unix
    # ... configuration based on type (see below)
```

**After adding, reload servers:**
```bash
curl -X POST http://127.0.0.1:5460/admin/reload-mcp -H 'Content-Type: application/json' -d '{}'
```


### Method 2: Environment Variable (Legacy)

Set `MCP_SERVERS` environment variable (comma-separated):
```bash
export MCP_SERVERS="server1=https://mcp1.com,server2=ws://127.0.0.1:7000"
```

**Note:** YAML config takes precedence over environment variables.


## Server Types & Configuration

### 1. Stdio (Local Process) - Most Common

Runs a local command/process that communicates via stdin/stdout.

**Example: NPM Package**
```yaml
mcp_servers:
  weather:
    type: stdio
    command: npx
    args:
      - -y
      - '@iflow-mcp/weather-mcp'
    env: {}  # Optional environment variables
```

**Example: Python Script**
```yaml
mcp_servers:
  project-memory:
    type: stdio
    command: /path/to/venv/bin/python
    args:
      - /path/to/memory_server.py
    env:
      SURREAL_URL: ws://127.0.0.1:8000/rpc
      SURREAL_USER: root
      SURREAL_PASS: root
```

**Example: Custom Binary**
```yaml
mcp_servers:
  my-tool:
    type: stdio
    command: /usr/local/bin/my-mcp-server
    args:
      - --config
      - /path/to/config.json
    env:
      API_KEY: your-key-here
```

**Fields:**
- `type: stdio` (required)
- `command: string` (required) - The executable to run
- `args: [string]` (optional) - Command-line arguments
- `env: {key: value}` (optional) - Environment variables

---

### 2. HTTP/HTTPS (Remote Server)

Connects to a remote HTTP endpoint.

```yaml
mcp_servers:
  my-api:
    type: http
    url: https://api.example.com/mcp
    token: optional-auth-token  # Or use env var MCP_TOKEN_MY_API
```

**Fields:**
- `type: http` (required)
- `url: string` (required) - Full URL to the MCP endpoint
- `token: string` (optional) - Auth token, or set `MCP_TOKEN_MY_API` env var

**Example with query params:**
```yaml
mcp_servers:
  exa:
    type: sse  # SSE is HTTP-based
    url: https://mcp.exa.ai/mcp
    query_params:
      exaApiKey: your-key-here
```

---

### 3. Server-Sent Events (SSE) - Remote

Similar to HTTP but uses SSE for streaming.

```yaml
mcp_servers:
  streaming-api:
    type: sse
    url: https://mcp.example.com/sse
    query_params:  # Optional
      apiKey: your-key
    token: optional-auth-token
```

**Fields:**
- `type: sse` (required)
- `url: string` (required)
- `query_params: {key: value}` (optional)
- `token: string` (optional)

---

### 4. WebSocket (WS/WSS) - Remote

Connects via WebSocket for real-time bidirectional communication.

```yaml
mcp_servers:
  realtime-server:
    type: ws
    url: wss://mcp.example.com/ws
    token: optional-auth-token
```

**Fields:**
- `type: ws` (required)
- `url: string` (required) - `ws://` or `wss://` URL
- `token: string` (optional)

---

### 5. Unix Socket (Local)

Connects to a local Unix domain socket.

```yaml
mcp_servers:
  local-socket:
    type: unix
    uds_path: /var/run/mcp.sock
    http_path: /mcp  # Optional, defaults to /mcp
```

**Fields:**
- `type: unix` (required)
- `uds_path: string` (required) - Path to Unix socket file
- `http_path: string` (optional) - HTTP path, defaults to `/mcp`

---

## Authentication

### Option 1: In Config File
```yaml
mcp_servers:
  my-server:
    type: http
    url: https://api.example.com/mcp
    token: your-token-here
```

### Option 2: Environment Variable (More Secure)
```yaml
mcp_servers:
  my-server:
    type: http
    url: https://api.example.com/mcp
    # token will be read from MCP_TOKEN_MY_SERVER env var
```

Set the environment variable:
```bash
export MCP_TOKEN_MY_SERVER="your-token-here"
```

**Naming:** `MCP_TOKEN_<SERVER_NAME>` (uppercase, underscores)

---

## Complete Examples

### Example 1: NPM Package (Stdio)
```yaml
mcp_servers:
  firecrawl-mcp:
    type: stdio
    command: npx
    args:
      - -y
      - firecrawl-mcp
    env:
      FIRECRAWL_API_KEY: your-api-key
```

### Example 2: Remote HTTP API
```yaml
mcp_servers:
  custom-api:
    type: http
    url: https://api.example.com/v1/mcp
    token: secret-token
```

### Example 3: Remote SSE with Query Params
```yaml
mcp_servers:
  exa-search:
    type: sse
    url: https://mcp.exa.ai/mcp
    query_params:
      exaApiKey: your-exa-key
```

### Example 4: WebSocket Server
```yaml
mcp_servers:
  realtime-data:
    type: ws
    url: wss://realtime.example.com/mcp
    token: ws-auth-token
```

### Example 5: Python Script with Environment
```yaml
mcp_servers:
  custom-tool:
    type: stdio
    command: /Users/bee/.venv/bin/python
    args:
      - /path/to/my_mcp_server.py
    env:
      DATABASE_URL: postgresql://localhost/mydb
      API_KEY: secret-key
      LOG_LEVEL: INFO
```

---

## After Adding a Server

### 1. Reload MCP Servers

**Via API:**
```bash
curl -X POST http://127.0.0.1:5460/admin/reload-mcp \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**Via Dashboard:**
- Go to **Overview** tab
- Click **"Reload MCP Servers"** button

### 2. Verify It's Loaded

**Check status:**
```bash
curl http://127.0.0.1:5460/admin/mcp/stdio/status | jq
```

**Or use troubleshooting script:**
```bash
./bin/troubleshoot.sh
```

**Or check dashboard:**
- Go to **Servers and Tools** tab
- Look for your server name

### 3. Test the Server

The server will be automatically tested when first used. You can also check:
- Circuit breaker status: `curl http://127.0.0.1:5460/admin/circuit-breaker/status | jq`
- Server diagnostics: `curl http://127.0.0.1:5460/admin/diagnostics/mcp/your-server-name | jq`

---

## Troubleshooting

### Server Not Appearing

1. **Check YAML syntax:**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
   ```

2. **Check logs:**
   ```bash
   tail -f ~/Library/Logs/ai/agent_runner.err.log | grep -i mcp
   ```

3. **Verify server name:**
   - No spaces or special characters (use underscores)
   - Must be unique

### Server Failing to Connect

1. **Check circuit breaker:**
   ```bash
   curl http://127.0.0.1:5460/admin/circuit-breaker/status | jq '.circuit_breakers."your-server"'
   ```

2. **For stdio servers:**
   - Verify command exists: `which npx` or `which python`
   - Check file permissions
   - Verify environment variables are set

3. **For remote servers:**
   - Test URL manually: `curl https://api.example.com/mcp`
   - Verify network connectivity
   - Check authentication token

4. **Reset circuit breaker:**
   ```bash
   curl -X POST http://127.0.0.1:5460/admin/circuit-breaker/reset \
     -H 'Content-Type: application/json' \
     -d '{"server": "your-server-name"}'
   ```

### Server Tools Not Available

1. **Wait for initialization:**
   - Stdio servers need a moment to start
   - Check `initialized: true` in status

2. **Check server health:**
   ```bash
   curl http://127.0.0.1:5460/admin/diagnostics/mcp/your-server-name | jq
   ```

3. **Reload servers:**
   - Sometimes a reload fixes tool discovery issues

---

## Best Practices

1. **Use YAML config** - Easier to manage than environment variables
2. **Store secrets in env vars** - Don't put tokens directly in config.yaml
3. **Test after adding** - Verify server appears and tools are available
4. **Monitor circuit breakers** - Use `./bin/troubleshoot.sh` regularly
5. **Use descriptive names** - `weather` not `w1` or `server-123`
6. **Document custom servers** - Add comments in config.yaml

---

## Finding MCP Servers

Popular MCP servers:
- **NPM Registry:** Search for `@modelcontextprotocol` packages
- **GitHub:** Search for "mcp-server" or "model context protocol"
- **MCP Directory:** https://modelcontextprotocol.io/servers

Common stdio servers:
- `npx -y @modelcontextprotocol/server-filesystem`
- `npx -y @modelcontextprotocol/server-puppeteer`
- `npx -y @playwright/mcp`
- `npx -y @iflow-mcp/weather-mcp`

---

## Quick Reference

| Type | Use Case | Example |
|------|----------|---------|
| `stdio` | Local npm packages, Python scripts, binaries | `npx -y firecrawl-mcp` |
| `http` | Remote REST APIs | `https://api.example.com/mcp` |
| `sse` | Remote streaming APIs | `https://mcp.exa.ai/mcp` |
| `ws` | Real-time bidirectional | `wss://realtime.example.com` |
| `unix` | Local socket servers | `/var/run/mcp.sock` |

---

## Need Help?

- Check logs: `tail -f ~/Library/Logs/ai/agent_runner.err.log`
- Run diagnostics: `./bin/troubleshoot.sh`
- Check dashboard: http://localhost:5455 (Servers and Tools tab)

