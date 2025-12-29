# Walkthrough: Fixing Agent Runner Imports and Type Safety

I have resolved the broken imports and type errors within the `agent_runner` module and its related services. The primary fix involved creating a compatibility shim to provide missing tool definitions and global instances.

## Core Changes

### 1. Compatibility Shim: [agent_runner.py](file:///Users/bee/Sync/Antigravity/ai/agent_runner/agent_runner.py) [NEW]
Created a new shim file to provide legacy constants and functions that were missing after the recent refactoring. This file now serves as the central point for:
- `FILE_TOOLS` and `MCP_TOOLS` definitions.
- `_agent_loop` compatibility function.
- `TASK_MODEL` and `AGENT_MODEL` constants.
- Shared global `AgentState` and `AgentEngine` instances.

### 2. Task Implementation: [weather_task_implementation.py](file:///Users/bee/Sync/Antigravity/ai/agent_runner/weather_task_implementation.py) [FIXED]
Refactored the weather task into a proper module.
- Added missing imports (`logging`, `json`, `TaskPriority`).
- Linked correctly to the `agent_runner` shim for `_agent_loop` and tool definitions.
- Added a `register_weather_task()` helper for easy integration.

### 3. Main Entrypoint: [main.py](file:///Users/bee/Sync/Antigravity/ai/agent_runner/main.py) [UPDATED]
Updated `main.py` to use the shared state and engine from the `agent_runner` shim. This ensures that background tasks and the FastAPI app are working with the exact same instances.

### 4. Background Tasks: [background_tasks.py](file:///Users/bee/Sync/Antigravity/ai/agent_runner/background_tasks.py) [FIXED]
- Resolved Mypy `truthy-function` errors by changing implicit boolean checks on functions to explicit `is not None` checks.
- Added missing type annotations for the `func` argument in the `Task` dataclass.

### 5. Service & Tool Fixes
#### [ollama_server.py](file:///Users/bee/Sync/Antigravity/ai/agent_runner/ollama_server.py)
- Fixed an incompatible type assignment for `request_id`.

#### [system_control_server.py](file:///Users/bee/Sync/Antigravity/ai/agent_runner/system_control_server.py)
- Fixed imports for `yaml` and `mcp` by adding `type: ignore`.
- Restored method signatures that were accidentally mangled.

#### [router/config.py](file:///Users/bee/Sync/Antigravity/ai/router/config.py)
- Added missing type annotation for `ollama_model_options`.

## Verification Results

### Import Resolution
All `NameError` and `ImportError` issues in the following files have been addressed:
- `weather_task_implementation.py`
- `task_loader.py`
- `task_factory.py`
- `main.py`

### Type Safety
Mypy errors related to `None` values, incompatible assignments, and untyped imports have been cleared or suppressed with `type: ignore` where appropriate for third-party libraries.

### System Consistency
By centralizing `state` and `engine` in the `agent_runner` shim, the system now maintains a consistent internal state across all components.

render_diffs(file:///Users/bee/Sync/Antigravity/ai/agent_runner/agent_runner.py)
render_diffs(file:///Users/bee/Sync/Antigravity/ai/agent_runner/weather_task_implementation.py)
render_diffs(file:///Users/bee/Sync/Antigravity/ai/agent_runner/main.py)
render_diffs(file:///Users/bee/Sync/Antigravity/ai/agent_runner/background_tasks.py)
