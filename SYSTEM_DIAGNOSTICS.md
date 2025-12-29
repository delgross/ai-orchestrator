# Antigravity System Diagnostics

This document logs identified problems and test failures discovered during the system-wide testing phase.

## Current Service Status
- **Router (5455)**: [x] Online (v0.8.0-sentinel)
- **Agent Runner (5460)**: [x] Online (v1.0.0-modular)
- **RAG Server (5555)**: [x] Online (Status: healthy)
- **Memory (SurrealDB)**: [x] Online (v2.4.0)
- **Ollama (11434)**: [x] Online (11 models discovered)

## Test Summaries

### Unit Tests
- `pytest tests/unit`: [x] PASS (17/17)
- `tests/unit/test_error_utils.py`: PASS
- `tests/unit/test_logging_utils.py`: PASS
- `tests/unit/test_unified_tracking_fix.py`: PASS

### Integration Tests
- `pytest tests/integration`: [x] PASS
- `tests/integration/test_router_api.py`: PASS
- `tests/integration/test_router_api_refactored.py`: PASS
- `bin/test_wizard_route.py` (Manual): [x] PASS (Status 200, Content: Pong)
- `bin/test_cloud_gpu.py` (Manual): [ ] FAIL (Script bug: `show_progress` argument error)

## Identified Problems

### 1. Dashboard - Frontend Initialization Failure
- **Symptom**: Dashboard hangs on "Loading Roles...", status values show "--", and indicators don't populate with text.
- **Log Reference**: Browser console: `TypeError: Cannot read properties of null (reading 'addEventListener')` at `app.js:534:47`.
- **Hypothesis**: `app.js` attempts to bind to `btn-save-config` which is missing from `index.html`. This uncaught error halts the `DOMContentLoaded` execution, preventing `fetchSystemRoles()` and other init functions from running.

### 2. Dashboard - Missing UI Elements
- **Symptom**: Config tab refers to manual save buttons and file selectors that don't exist in the HTML.
- **Hypothesis**: The HTML template in `index.html` is out of sync with the logic in `app.js`.

### 3. Dashboard - Layout Issues (Clock)
- **Symptom**: Clock position and potential duplicates.
- **Current State**: Clock is inside the `brand` div at the top left. User wants it moved and cleaned up.

### 4. Dashboard - Placeholder Metrics
- **Symptom**: Metrics cards show static CSS placeholders (0%) instead of real data, even though `/admin/observability/stats` returns valid metrics.
- **Hypothesis**: Logic to map backend metrics to DOM elements is likely being halted by the JS crash mentioned in Problem #1.

### 5. Backend - Circuit Breaker Reporting
- **Symptom**: Browser subagent noted "Success"/ "Failures" counters but indicators are not always accurate.
- **Verification**: `/admin/circuit-breaker/status` confirms backend tracking is active, but frontend rendering needs verification.

### 6. Configuration - Hardcoded Path Errors
- **Symptom**: Runtime changes to models are not persisted across service restarts.
- **Log Reference**: `agent_runner/state.py:43` and `agent_runner/main.py:391`.
- **Hypothesis**: The code uses `Path("ai/system_config.json")` which, when combined with `os.getcwd()`, points to `ai/ai/system_config.json`. The correct path should likely be `system_config.json` in the project root.

### 7. API - Inconsistent Model Management
- **Symptom**: Multiple endpoints exist for updating models (`/admin/roles` vs `/admin/config/models`) with different levels of persistence and mapping.
- **Hypothesis**: Structural debt in the admin API needs consolidation. One endpoint handles runtime assignment while the other handles persistence, creating a disjointed user experience.
