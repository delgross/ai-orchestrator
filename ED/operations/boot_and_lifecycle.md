# Boot Process & Lifecycle

**Antigravity** implements a rigorous, formalized boot sequence designed to ensure stability and observability. The core philosophy is "Crash Mitigation" — the system prefers to start in a degraded state rather than fail to start at all.

**Source**: `ai/agent_runner/main.py`
**Log**: `ai/logs/startup_issues.log`

---

## 1. The 7-Step Boot Sequence

The `on_startup()` routine executes distinct phases, logging progress to the frontend via `_send_startup_monitor_message`.

| Step | phase | Description |
| :--- | :--- | :--- |
| **0/7** | **Validation** | Checks Python version, dependencies, and environment health using `startup_validator.py`. |
| **1/7** | **State Init** | Initializes `AgentState` object, loads modes, sets up defaults. |
| **2/7** | **Memory Connect** | Connects to SurrealDB. Retries 5 times. Enters **Degraded Mode** if failed. |
| **3/7** | **Config Sync** | `ConfigManager` syncs Authority Chain (DB > RAM > Disk). |
| **4/7** | **Service Registry** | Initializes `ServiceRegistry` and discovers services. |
| **5/7** | **MCP Loading** | Loads MCP servers. Uses `ConfigManager` to populate DB if empty. |
| **6/7** | **Health Check** | Verifies internet connectivity and critical route availability. |
| **7/7** | **Ready** | System opens Nexus gates for traffic. |

---

## 2. Degraded Mode

The system tracks failures in `state.degraded_reasons`.

- **Scenario**: SurrealDB is down.
- **Behavior**:
    1.  `[BOOT_STEP] 2/7` fails after retries.
    2.  Sets `state.memory = None`.
    3.  Adds `"memory"` to `state.degraded_features`.
    4.  Logic elsewhere checks `if state.memory:` before attempting DB calls.
    5.  Status LED on dashboard turns Yellow/Orange instead of Green.

---

## 3. Optimization Techniques

- **Cache Clearing**: Aggressively removes `__pycache__` and `.pyc` files on startup (unless disabled) to prevent "ghost code" issues during rapid development.
- **Parallel Sync**: The `ConfigManager` performs file timestamp checks in parallel `asyncio.gather` tasks to reduce IO blocking.
- **Lazy Loading**: Heavy libraries (like `logfire` or `pydantic_ai`) are imported only inside try/except blocks or specific functions, not at module level.

---

## 4. Signal Handling

The `lifespan` context manager handles graceful shutdown:
1.  **Stop**: Received SIGINT/SIGTERM.
2.  **Drain**: Finishes active tasks (where possible).
3.  **Disconnect**: Closes HTTP clients and DB connections.
4.  **Cleanup**: Removes temporary sockets or logs.
