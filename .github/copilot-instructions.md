## Antigravity AI Orchestrator — AI Agent Guide
- **Prime directive**: Never crash; degrade. On any failure, log, add to `startup_issues`/`startup_warnings`, prefer reduced capability over abort.
- **Core services**: Router :5455, Agent Runner :5460, RAG :5555, SurrealDB :8000. Chat I/O funnels through Nexus in [agent_runner/nexus.py](agent_runner/nexus.py); keep it the single ingress/egress.
- **Chat fast path**: Messages ≤4 words without actions skip the agent loop in `Nexus.dispatch` for instant replies—preserve this optimization.

## Architecture & Control Flow
- **Entry chain**: Router → Nexus → Engine/Intent → Tool selection → MCP execution → Streaming reply. Avoid bypassing Nexus when adding features.
- **Boot sequence** in [agent_runner/main.py](agent_runner/main.py) logs `[BOOT_STEP] 0-7`; do not reorder without matching degraded fallbacks. Step 6 spawns [rag_server.py](rag_server.py).
- **Configuration authority**: SurrealDB `config_state` > AgentState cache > disk (`config/*.yaml`, `.env`). Use [agent_runner/config_manager.py](agent_runner/config_manager.py) to sync; `.env` must be ingested via `sync_env_from_disk`, not imported directly.
- **Filesystem sandbox**: Operate only inside `state.agent_fs_root` (default `~/ai/agent_fs_root`); tool paths should respect this boundary.
- **Intent/Tool selection**: [agent_runner/intent.py](agent_runner/intent.py) and Maître d’ cache throttle the MCP tool set to prevent context bloat. Use the classifier rather than hard-coding tool lists.

## Resilience & Safety Patterns
- **Circuit breakers**: Check `state.mcp_circuit_breaker` before calling MCP servers; auto-disable unhealthy servers instead of retry storms.
- **Unified tracking**: Emit events through [common/unified_tracking.py](common/unified_tracking.py) for observability and dashboards.
- **Internet awareness**: Consult `state.internet_available`; fall back to `state.fallback_model` (Ollama) when offline to maintain service.
- **Gravity mode**: If SurrealDB or RAG is down, continue in degraded mode (no memory/RAG) rather than failing requests.

## Configuration & Secrets
- Shared loader lives in [config](config/README.md); env vars override service `.env` files (`router.env`, `agent_runner/agent_runner.env`). Future `config.yaml` is planned but not authoritative yet.
- Avoid ad-hoc `os.getenv` reads in services—route through the loader so precedence is preserved.

## Developer Workflows
- **Start/stop**: `./manage.sh start|status|logs` handles all services and environment detection.
- **Tests**: `./test.sh` runs pytest-based unit/integration suites; prefer it over raw pytest to match env flags.
- **Auth quirks**: Router auth propagation is fragile (see [overview](overview.md)); when touching internal calls, ensure router tokens flow or expect hydration hangs.

## Data & Memory
- Memory and knowledge live in SurrealDB; vector/RAG operations come from [rag_server.py](rag_server.py). When memory is unavailable, system should mark degraded and skip hydration instead of blocking.
- Tool results and config ingestion sync through the memory server—avoid direct DB writes outside the managers.

## Style & Persona (Prompts)
- Follow persona rules in [agent_runner/prompts.py](agent_runner/prompts.py): fast, concise, no tool narration, warm tone.
- Keep streaming-friendly responses (short, incremental) to preserve low latency paths highlighted in [overview.md](overview.md).

## When Changing Startup Logic
- Maintain the 7-step order and logging; each step’s failure must set `state.degraded_reasons` and continue where safe.
- Background tasks and internet checks run in [background_tasks.py](agent_runner/background_tasks.py); avoid duplicating health probes.

## RAG/Tooling Notes
- MCP registry integrity is validated at boot; new tools must register through existing registry flows, not ad-hoc imports.
- For new ingestion flows, reuse chunking/indexing in [rag_server.py](rag_server.py) and keep vector writes behind existing helpers.

## Quick References
- Architecture deep dives: [ED/architecture](ED/architecture) and [overview.md](overview.md) for constraints and pain signals.
- Operations docs: [ED/operations](ED/operations) for boot, lifecycle, and config authority chain.

