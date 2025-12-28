# Circuit Breaker Design Issues

**Date:** 2025-12-25  
**Status:** Analysis Complete - Issues Identified

---

## Executive Summary

The circuit breaker implementation has several design flaws that prevent proper recovery and create unnecessary downtime:

1. **Recovery test doesn't use actual code path** - Fragile manual testing
2. **No half-open state** - Goes directly from disabled to enabled
3. **Success reset doesn't help disabled servers** - Check happens before call
4. **Recovery test is complex and error-prone** - Manual RPC message handling
5. **Race conditions** - Server can recover between check and call

---

## Issues Identified

### 🔴 **CRITICAL: Recovery Test Doesn't Use Actual Code Path**

**Problem:**
The recovery test in `health_monitor.py` manually tests stdio servers by:
- Importing `_STDIO_PROCESSES` directly (fragile, can fail)
- Manually sending RPC messages (bypasses all the retry/reconnect logic)
- Doesn't use `tool_mcp_proxy()` which has all the proper error handling

**Current Code:**
```python
# health_monitor.py:112-130
from agent_runner.agent_runner import _STDIO_PROCESSES
if server in _STDIO_PROCESSES:
    proc = _STDIO_PROCESSES[server]
    # Manually send test RPC...
    test_line = json.dumps(test_rpc) + "\n"
    proc.stdin.write(test_line.encode("utf-8"))
```

**Impact:**
- Recovery test may pass even though normal requests would fail
- Recovery test may fail even though normal requests would work
- Doesn't test the actual code path users experience
- Fragile - import can fail, process state can be stale

**Recommendation:**
Use `tool_mcp_proxy()` with a bypass flag for recovery testing.

---

### 🔴 **CRITICAL: No Half-Open State**

**Problem:**
Circuit breaker goes directly from "disabled" → "enabled" without testing a single request first.

**Current Behavior:**
```python
# health_monitor.py:170-174
if test_success:
    cb["failures"] = 0
    cb["disabled_until"] = 0.0  # Fully enabled immediately
```

**Impact:**
- If recovery test passes but server is still flaky, it immediately fails again
- No gradual recovery - all-or-nothing
- Can cause rapid disable/re-enable cycles

**Recommendation:**
Implement half-open state: allow one test request, if it succeeds, fully enable.

---

### 🟡 **MODERATE: Success Reset Doesn't Help Disabled Servers**

**Problem:**
When a call succeeds, `_reset_mcp_success()` resets the circuit breaker:
```python
def _reset_mcp_success(server: str) -> None:
    cb["failures"] = 0
    cb["disabled_until"] = 0.0
```

But the circuit breaker check happens **before** the call:
```python
# tool_mcp_proxy:2027-2032
cb = MCP_CIRCUIT_BREAKER.get(server, {})
disabled_until = cb.get("disabled_until", 0.0)
if disabled_until > time.time():
    return {"ok": False, "error": "circuit breaker active"}
# ... make call ...
_reset_mcp_success(server)  # Never reached if disabled
```

**Impact:**
- If server is disabled, successful calls can't happen to reset it
- Only recovery test can re-enable (runs every 60 seconds)
- Creates unnecessary delay in recovery

**Recommendation:**
Allow one test request even when disabled (half-open state).

---

### 🟡 **MODERATE: Recovery Test Complexity**

**Problem:**
Recovery test has complex logic for different schemes:
- Stdio: Manual process access, RPC sending
- HTTP: Direct HTTP calls
- WebSocket: Skipped (assumes OK)
- Unix: Simplified (assumes OK)

**Impact:**
- Different code paths for testing vs. normal operation
- More bugs, harder to maintain
- Inconsistent behavior

**Recommendation:**
Use unified `tool_mcp_proxy()` for all recovery tests.

---

### 🟡 **MODERATE: Race Conditions**

**Problem:**
1. Circuit breaker check happens at start of `tool_mcp_proxy`
2. Server could recover between check and actual call
3. If call succeeds, circuit breaker is reset
4. But if server was disabled, check prevents the call

**Impact:**
- Server may be healthy but still blocked
- Recovery depends on timing of health check task

**Recommendation:**
Implement half-open state to allow test requests.

---

## Recommended Fixes

### 1. **Use `tool_mcp_proxy()` for Recovery Testing**

```python
async def test_circuit_breaker_recovery() -> None:
    """Test disabled servers using actual code path."""
    for server, cb in _mcp_circuit_breaker.items():
        if disabled_until <= now and failures > 0:
            # Temporarily bypass circuit breaker for test
            # Use actual tool_mcp_proxy with bypass flag
            res = await tool_mcp_proxy(
                server=server,
                tool="check_health",  # or tools/list
                arguments={},
                bypass_circuit_breaker=True  # New flag
            )
            if res.get("ok"):
                # Enter half-open state or fully enable
                ...
```

### 2. **Implement Half-Open State**

```python
# Add to circuit breaker state
cb["state"] = "closed" | "open" | "half_open"
cb["half_open_test_count"] = 0

# In tool_mcp_proxy:
if cb["state"] == "open" and disabled_until <= now:
    # Allow one test request
    cb["state"] = "half_open"
    cb["half_open_test_count"] = 1

if cb["state"] == "half_open":
    if success:
        cb["state"] = "closed"
        cb["failures"] = 0
    else:
        cb["state"] = "open"
        cb["disabled_until"] = time.time() + 300
```

### 3. **Simplify Recovery Test**

Remove all manual RPC handling, use `tool_mcp_proxy()` for all schemes.

---

## Priority

1. **HIGH**: Use `tool_mcp_proxy()` for recovery testing
2. **MEDIUM**: Implement half-open state
3. **LOW**: Simplify recovery test code

---

## Impact Assessment

**Current State:**
- Servers can be disabled for 5+ minutes even if they recover quickly
- Recovery depends on health check task timing (every 60s)
- Fragile recovery test may not accurately reflect server health

**After Fixes:**
- Faster recovery (half-open allows immediate test)
- More reliable recovery (uses actual code path)
- Simpler code (unified testing approach)




