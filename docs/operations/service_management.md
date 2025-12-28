# ⚙️ Service Management Guide

The AI Orchestrator uses a central management script and macOS `launchd` for service lifecycle management.

## 🚀 The `manage.sh` Script
Located at the project root, `manage.sh` is your primary interface for controlling the system.

### Core Commands
- `./manage.sh status`: Check the health and PIDs of Router, Agent Runner, and SurrealDB.
- `./manage.sh start`: Start all services (using `launchd` where configured).
- `./manage.sh stop`: Gracefully stop all services.
- `./manage.sh restart`: Restart the entire stack.
- `./manage.sh ensure`: Verify services are running and start any that are missing.

---

## 🛠️ Service Architecture
- **Router (Port 5455)**: Managed by `local.ai.router.plist`.
- **Agent Runner (Port 5460)**: Managed by `local.ai.agent_runner.plist`.
- **SurrealDB (Port 8000)**: Typically started as a direct process by `manage.sh start`.

## 📜 Logs
Logs are stored in `~/Library/Logs/ai/`:
- `router.out.log` / `router.err.log`
- `agent_runner.out.log` / `agent_runner.err.log`

## 🔄 Automatic Restarts
Services managed by `launchd` will automatically restart if they crash, as `KeepAlive` is set to `true` in their plists.
