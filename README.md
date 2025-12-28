# AI Orchestrator

A local AI orchestration system that routes requests to multiple LLM providers, manages agent tools, MCP servers, and provides a unified OpenAI-compatible API.

## Architecture

```
┌─────────────┐
│  Frontend   │  (LibreChat, Open WebUI, or any OpenAI-compatible client)
│  (Port 3080)│
└──────┬──────┘
       │
       │ OpenAI-compatible API
       │
┌──────▼──────────────────────────────────────┐
│         Router (Port 5455)                   │
│  - Routes to providers (Ollama, OpenAI, etc)│
│  - Routes to agent-runner for tool-enabled  │
│  - Routes to RAG backend                    │
│  - Serves dashboard at /dashboard            │
└──────┬──────────────────────────────────────┘
       │
       ├──► Ollama (Port 11434)
       ├──► OpenAI/OpenRouter/etc (via providers.yaml)
       ├──► Agent Runner (Port 5460) ──► Tools + MCP + RAG + DB
       └──► RAG Backend (configurable)
```

## Quick Start

### 1. Initial Setup

```bash
cd ~/Sync/Antigravity/ai

# Set up launchd services (one-time)
./setup_launchd.sh

# Start all services
./manage.sh ensure
```

### 2. Check Status

```bash
./manage.sh status
```

### 3. Access Dashboard

Open http://127.0.0.1:5455/dashboard in your browser.

## Services

### Router (Port 5455)

- **Purpose**: Main API gateway that routes requests to different providers
- **Endpoints**:
  - `GET /` - Health check and status
  - `GET /dashboard` - Web dashboard
  - `GET /v1/models` - List available models
  - `POST /v1/chat/completions` - Chat completions (OpenAI-compatible)
  - `POST /admin/reload` - Reload providers config

**Configuration**: `router.env`, `providers.yaml`, `providers.env`

### Agent Runner (Port 5460)

- **Purpose**: Tool-enabled agent that can use files, MCP servers, RAG, and database
- **Capabilities**:
  - File operations (read, write, list, move, delete) in sandboxed workspace
  - MCP server integration (HTTP, WebSocket, Unix socket, stdio)
  - RAG integration (via router)
  - Database access (via db_client.py)

**Configuration**: `agent_runner/agent_runner.env`

**Models**: Use `agent:mcp` to access the agent with tools enabled.

## Configuration

### Router Configuration

**`router.env`**:
```bash
OLLAMA_BASE=http://127.0.0.1:11434
AGENT_RUNNER_URL=http://127.0.0.1:5460
RAG_BASE=http://127.0.0.1:5555  # Optional
RAG_QUERY_PATH=/query
ROUTER_AUTH_TOKEN=your-token-here  # Optional, for LAN access
ROUTER_MAX_CONCURRENCY=10  # Optional, limit concurrent requests
```

**`providers.yaml`**:
```yaml
providers:
  openai:
    type: openai_compat
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
  openrouter:
    type: openai_compat
    base_url: https://openrouter.ai/api/v1
    api_key_env: OPENROUTER_API_KEY
```

**`providers.env`** (API keys):
```bash
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
```

### Agent Runner Configuration

**`agent_runner/agent_runner.env`**:
```bash
# The model that does reasoning (can be any provider:model)
AGENT_MODEL=openai:gpt-4.1-mini

# MCP servers (optional)
MCP_SERVERS="weather=https://mcp-weather.com/mcp,local=ws://127.0.0.1:7000"

# MCP tokens (optional, per server)
MCP_TOKEN_WEATHER="your-token"

# File sandbox root
AGENT_FS_ROOT=~/ai/agent_fs_root

# Limits
AGENT_MAX_READ_BYTES=200000
AGENT_MAX_TOOL_STEPS=8
```

## Management Scripts

### `manage.sh` - Main Control Script

```bash
./manage.sh status      # Check what's running
./manage.sh ensure      # Start any missing services
./manage.sh start       # Start all services
./manage.sh stop        # Stop all services
./manage.sh restart     # Restart all services
```

### Helper Scripts

**`bin/set_agent_model.sh <model>`**
- Change the agent's reasoning model
- Example: `./bin/set_agent_model.sh ollama:llama3.1`

**`bin/set_router_token.sh <token>`**
- Set router authentication token for LAN access

**`bin/set_mcp_servers.sh "name=url,..."`**
- Configure MCP servers
- Example: `./bin/set_mcp_servers.sh "weather=https://mcp-weather.com/mcp"`

**`bin/set_rag_backend.sh <url> [path]`**
- Configure RAG backend
- Example: `./bin/set_rag_backend.sh http://127.0.0.1:5555 /query`

## Model Routing

Models are routed by prefix:

- **`agent:mcp`** → Agent-runner with tools (files, MCP, RAG, DB)
- **`ollama:llama3`** → Direct Ollama (no tools)
- **`openai:gpt-4.1-mini`** → OpenAI API (no tools)
- **`openrouter:meta-llama/llama-3.1-8b-instruct`** → OpenRouter (no tools)
- **`rag:index-name`** → RAG backend (if configured)

## MCP Server Support

The agent-runner supports MCP servers via multiple transports:

- **HTTP/HTTPS**: `https://mcp-server.com/mcp`
- **WebSocket**: `ws://127.0.0.1:7000` or `wss://mcp-server.com`
- **Unix Socket**: `unix:/var/run/mcp.sock|/mcp` (path after `|` is optional)
- **Stdio**: `stdio:npx @modelcontextprotocol/server-filesystem`

Configure in `agent_runner/agent_runner.env`:
```bash
MCP_SERVERS="server1=https://mcp1.com,server2=ws://127.0.0.1:7000"
MCP_TOKEN_SERVER1="token-if-needed"
```

## Logging

Logs are written to:
- Router: `~/Library/Logs/ai/router.{out,err}.log`
- Agent-runner: `~/Library/Logs/ai/agent_runner.{out,err}.log`

Structured JSON events are logged with `JSON_EVENT:` prefix for AI log analysis:
- `JSON_EVENT: {"event":"gateway_error",...}`
- `JSON_EVENT: {"event":"tool_error",...}`
- `JSON_EVENT: {"event":"mcp_error",...}`

## LibreChat Setup (Optional)

### Using Docker Compose

```bash
# Prepare for Portainer or local Docker
./librechat-portainer-prep.sh

# Or use local Docker Compose
./librechat-setup.sh
docker compose -f librechat-docker-compose.yaml up -d
```

### Using Portainer

1. Run `./librechat-portainer-prep.sh` to generate secrets
2. Copy contents of `librechat-docker-compose-portainer.yaml`
3. In Portainer: Stacks → Add stack → Web editor → Paste → Deploy
4. Access at http://localhost:3080
5. Configure endpoint: Settings → Endpoints → Add
   - Name: `AI Orchestrator`
   - Base URL: `http://host.docker.internal:5455/v1`
   - Models: `agent:mcp`, `ollama:llama3`, etc.

## File Structure

```
ai/
├── router/              # Router service (FastAPI)
│   └── router.py
├── agent_runner/        # Agent service (FastAPI)
│   ├── agent_runner.py
│   ├── agent_runner.env
│   └── db_client.py
├── dashboard/           # Web dashboard
│   └── index.html
├── bin/                 # Helper scripts
│   ├── run_router.sh
│   ├── run_agent_runner.sh
│   ├── set_agent_model.sh
│   └── ...
├── configs/             # Configuration files
├── providers.yaml       # Provider definitions
├── providers.env        # Provider API keys
├── router.env           # Router configuration
├── manage.sh            # Main management script
├── setup_launchd.sh     # Setup launchd services
└── README.md            # This file
```

## Ports

- **5455**: Router (main API gateway)
- **5460**: Agent-runner (tool-enabled agent)
- **3080**: LibreChat (frontend + backend, if installed)
- **27017**: MongoDB (if LibreChat installed)
- **7700**: Meilisearch (if LibreChat installed)
- **6379**: Redis (if LibreChat installed)

## Auto-Start on Reboot

Services are configured to auto-start via launchd:

- Plists: `~/Library/LaunchAgents/local.ai.{router,agent_runner}.plist`
- Setup: Run `./setup_launchd.sh` once
- They will start automatically on login/reboot

## Troubleshooting

### Services not starting

```bash
# Check status
./manage.sh status

# Check logs
tail -f ~/Library/Logs/ai/router.err.log
tail -f ~/Library/Logs/ai/agent_runner.err.log

# Restart services
./manage.sh restart
```

### Port conflicts

```bash
# See what's using ports
lsof -i :5455
lsof -i :5460

# Stop everything
./manage.sh stop
./terminate_everything.sh
```

### Dashboard shows agent-runner as down

- Check if agent-runner is running: `./manage.sh status`
- Check browser console for CORS errors
- Verify agent-runner is accessible: `curl http://127.0.0.1:5460/`

## Development

### Running manually (without launchd)

```bash
# Router
cd ~/Sync/Antigravity/ai
./bin/run_router.sh

# Agent-runner
cd ~/Sync/Antigravity/ai
./bin/run_agent_runner.sh
```

### Testing API

```bash
# List models
curl http://127.0.0.1:5455/v1/models

# Chat with agent
curl http://127.0.0.1:5455/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agent:mcp",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Security Notes

- Router auth token is optional but recommended for LAN access
- Agent file operations are sandboxed to `AGENT_FS_ROOT`
- MCP tokens are stored in `agent_runner.env` (keep secure)
- Provider API keys are in `providers.env` (keep secure)

## License

[Your license here]
