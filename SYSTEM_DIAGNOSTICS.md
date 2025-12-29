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

### 1. Dashboard - Frontend Initialization Failure (FIXED)
- **Fix**: Added null checks to `app.js` and synchronized `index.html` to include missing components. Initialization now completes successfully.

### 2. Dashboard - Missing UI Elements (FIXED)
- **Fix**: Added **File Manager** (selector and save buttons) to the Config tab.

### 3. Dashboard - Layout Issues (Clock) (FIXED)
- **Fix**: Clock repositioned correctly in header and redundant styles removed.

### 4. Dashboard - Placeholder Metrics (FIXED)
- **Fix**: Mapping logic in `app.js` updated to match backend JSON schema.

### 5. Backend - Circuit Breaker Reporting (VERIFIED)
- **Status**: Operational. Indicators now correctly reflect backend states.

### 6. Configuration - Hardcoded Path Errors (FIXED)
- **Fix**: Updated `agent_runner/state.py` and `main.py` to use absolute paths relative to project root. Persistence verified.

### 7. API - Inconsistent Model Management (FIXED)
- **Fix**: Consolidated model updates under `save_system_config()` helper. Runtime changes now persist automatically.

### 8. RAG Ingestion & Night Agent (OPERATIONAL)
- **Ingestion**: Currently 3 files in `deferred` (m4a, pdf, txt). Night shift synchronized (1 AM - 6 AM).
- **Tasks**: Duplicate registrations for research/briefing tasks removed from `main.py`.
- **Economic Safety**: OCR/Vision tasks now use `gpt-4o-mini` by default.
