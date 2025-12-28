# System Capabilities Reference

This document tracks the capabilities of the Router and Agent-Runner services.

## Quick Discovery

### Router (Port 5455)
- **API Docs**: http://127.0.0.1:5455/docs (FastAPI automatic OpenAPI docs)
- **Root Info**: `GET /` - Returns service info, providers, config
- **Health**: `GET /health` - Health check

### Agent-Runner (Port 5460)
- **API Docs**: http://127.0.0.1:5460/docs (FastAPI automatic OpenAPI docs)
- **Root Info**: `GET /` - Returns service info, tools, MCP servers
- **Health**: `GET /admin/health` - Comprehensive health check

## Router Capabilities

### Core Endpoints
- `GET /` - Service info and status
- `GET /health` - Health check
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completions (OpenAI-compatible)
- `GET /dashboard` - Web dashboard
- `GET /docs` - Interactive API documentation (OpenAPI/Swagger)

### Admin Endpoints (Require Auth Token)
- `POST /admin/reload` - Reload providers configuration
- `POST /admin/cache/clear` - Clear models cache
- `POST /admin/start-router` - Start router service
- `POST /admin/stop-router` - Stop router service
- `POST /admin/restart-router` - Restart router service
- `POST /admin/start-agent` - Start agent-runner service
- `POST /admin/stop-agent` - Stop agent-runner service
- `POST /admin/restart-agent` - Restart agent-runner service
- `POST /admin/restart-all` - Restart all services
- `POST /admin/reload-providers` - Reload providers.yaml
- `GET /admin/mcp-toggle` - Get MCP tool access status
- `POST /admin/mcp-toggle` - Enable/disable MCP tool access
- `GET /admin/active-model` - Get active model
- `POST /admin/active-model` - Set active model

### Metrics & Monitoring
- `GET /metrics` - Usage metrics and statistics

## Agent-Runner Capabilities

### Core Endpoints
- `GET /` - Service info, tools, MCP servers
- `GET /admin/health` - Comprehensive health check (gateway, MCP servers, memory, dashboard)
- `GET /metrics` - Agent metrics and statistics
- `POST /v1/chat/completions` - Chat completions with tools

### Admin Endpoints
- `GET /admin/system-status` - System status (idle detection, load, active requests)
- `GET /admin/memory` - Memory/knowledge graph facts
- `GET /admin/memory/stats` - Memory statistics
- `GET /admin/background-tasks` - Background task status and schedule
- `POST /admin/background-tasks/{task_name}/enable` - Enable a task
- `POST /admin/background-tasks/{task_name}/disable` - Disable a task
- `POST /admin/background-tasks/{task_name}/trigger` - Manually trigger a task
- `GET /admin/mcp/intel` - MCP server intelligence
- `GET /admin/diagnostics` - System diagnostics
- `GET /admin/diagnostics/mcp/{server}` - MCP server diagnostics
- `GET /admin/config` - Configuration summary
- `GET /admin/performance` - Performance metrics
- `GET /admin/dev/logs` - Development logs
- `POST /admin/dev/clear-cache` - Clear internal caches
- `GET /admin/notifications` - System notifications
- `GET /admin/sanity/check` - Sanity check

### File Tools
- `list_dir` - List directory contents
- `path_info` - Get file/directory info
- `read_text` - Read text file
- `write_text` - Write text file
- `append_text` - Append to text file
- `make_dir` - Create directory
- `remove_file` - Delete file
- `move_path` - Move/rename file or directory
- `remove_dir` - Delete directory
- `copy_file` - Copy file
- `copy_path` - Copy file or directory recursively
- `find_files` - Search for files
- `batch_operations` - Batch file operations
- `watch_path` - Watch file/directory for changes

### MCP Tools
- All tools from configured MCP servers (weather, memory, search, etc.)
- Tools are prefixed with `mcp__{server}__{tool_name}`

## Background Tasks

### Built-in Tasks
- `health_check` - Periodic health monitoring
- `comprehensive_health_check` - Full system health check
- `internet_check` - Internet connectivity monitoring
- `research_cycle` - MCP intelligence gathering
- `intel_consolidation` - Intelligence consolidation
- `log_cleanup` - Log file cleanup
- `mcp_reload` - MCP server reload
- `memory_fact_stats` - Memory statistics collection
- `surreal_backup` - Database backup

### Configurable Tasks
- Tasks defined in `config.yaml` under `agent_runner.periodic_tasks`
- Can use local Ollama models
- Support MCP servers or simple file operations

## How to Discover Capabilities

### Method 1: Interactive API Docs (Best)
1. Open http://127.0.0.1:5455/docs (Router)
2. Open http://127.0.0.1:5460/docs (Agent-Runner)
3. Browse all endpoints, try them out, see schemas

### Method 2: Root Endpoints
```bash
# Router capabilities
curl http://127.0.0.1:5455/ | jq

# Agent-Runner capabilities
curl http://127.0.0.1:5460/ | jq
```

### Method 3: This Document
- This file tracks all capabilities
- Update when new features are added

## Configuration

### Router Config
- Location: `config/config.yaml` (router section)
- Environment: `router.env`
- Key settings: `auth_token`, `max_concurrency`, `providers_yaml`

### Agent-Runner Config
- Location: `config/config.yaml` (agent section)
- Environment: `agent_runner/agent_runner.env`
- Key settings: `model`, `tasks.model`, `fs_root`, `mcp_servers`

## Last Updated
Generated automatically - check `/docs` endpoints for latest API schemas.






