# MCP Server Resilience & Robustness Evaluation

**Date:** 2025-12-24  
**Goal:** Evaluate current system's ability to keep as many MCP servers (local and remote) available to the orchestrator as possible

---

## Executive Summary

The current system has **basic resilience mechanisms** but several **critical vulnerabilities** that can cause cascading failures and prevent servers from remaining available. The system treats local and remote servers identically, which is problematic since they have different failure modes and recovery characteristics.

**Overall Resilience Score: 6/10**

---

## Current Resilience Mechanisms

### ✅ Strengths

1. **Circuit Breaker Pattern**
   - Prevents repeated failures from overwhelming the system
   - Threshold: 3 consecutive failures → 5-minute disable
   - Per-server isolation (one server's failures don't directly disable others)

2. **Automatic Recovery Testing**
   - `test_circuit_breaker_recovery()` runs periodically
   - Resets circuit breaker after timeout expires
   - **However:** Only reduces failure count by 1, doesn't actually test if server recovered

3. **Error Logging & Monitoring**
   - Comprehensive JSON event logging for all failure types
   - Health monitoring task tracks server status
   - Notifications for critical issues

4. **Manual Recovery Options**
   - `/admin/reload-mcp` endpoint resets all circuit breakers
   - Allows manual intervention when needed

5. **Concurrency Protection**
   - Semaphore limits concurrent stdio subprocess creation (max 5)
   - Prevents file handle exhaustion

---

## Critical Vulnerabilities

### 🔴 **CRITICAL: Local Stdio Servers Are Per-Request Spawned**

**Problem:**
- Every MCP stdio server call spawns a new subprocess
- Process is killed immediately after request completes (`proc.kill()` in finally block)
- **No persistent connections** - each request pays full startup cost

**Impact:**
- **High latency** - every call requires process spawn + initialize handshake
- **Resource waste** - repeated process creation/destruction
- **No state preservation** - servers can't maintain state between calls
- **Vulnerable to spawn failures** - if system is under load, new processes may fail to spawn

**When Agent-Runner Hangs:**
- If agent-runner becomes unresponsive, **ALL local stdio servers become unavailable**
- No way to access local servers independently
- Local servers are completely dependent on agent-runner process

**Recommendation:** Implement persistent process management for local stdio servers

---

### 🟡 **MODERATE: No Distinction Between Local and Remote Servers**

**Problem:**
- Circuit breaker treats all servers identically (3 failures → 5 min disable)
- Local servers (stdio) have different failure modes than remote (http/ws/sse)
- However, per-server isolation already exists (one server's failures don't disable others)

**Current Behavior:**
```python
# Same circuit breaker logic for ALL servers
FAILURE_THRESHOLD = 3
DISABLE_DURATION = 300  # 5 minutes
```

**Impact:**
- Network hiccup affecting remote server → local servers unaffected (good) ✅
- If agent-runner has issues spawning local processes, they all fail together
- **Note:** User preference is to keep same circuit breaker logic for all servers

**Status:** This is working as intended - per-server isolation provides sufficient protection

---

### 🔴 **CRITICAL: Circuit Breaker Recovery Doesn't Actually Test Recovery**

**Problem:**
```python
# health_monitor.py:89-90
cb["failures"] = max(0, cb["failures"] - 1)  # Reduce failure count
cb["disabled_until"] = 0.0  # Allow retry
```

**Impact:**
- Recovery test just resets the breaker without verifying server is actually working
- Server may still be broken, causing immediate re-failure
- No gradual recovery (half-open state)

**Recommendation:** Implement actual health check before resetting circuit breaker

---

### 🟡 **MODERATE: No Isolation When Agent-Runner Has Issues**

**Problem:**
- If agent-runner process hangs or becomes unresponsive:
  - Router detects this and can disable MCP access globally
  - But agent-runner itself may still be running (just hung)
  - All local stdio servers become unavailable even though they could work

**Current Router Behavior:**
```python
# router/router.py:593-621
async def _monitor_agent_runner_health():
    # Detects unresponsiveness
    # Sends notifications
    # But doesn't distinguish between "agent-runner dead" vs "agent-runner hung"
```

**Impact:**
- If agent-runner is hung but process alive, local servers are blocked
- No way to access local servers independently
- Router's `mcp_tool_access_enabled` toggle is all-or-nothing

**Recommendation:** Consider making local stdio servers independent of agent-runner HTTP interface

---

### 🟡 **MODERATE: Single Point of Failure in Subprocess Semaphore**

**Problem:**
```python
_MCP_SUBPROCESS_SEMAPHORE = asyncio.Semaphore(5)  # Max 5 concurrent subprocesses
```

**Impact:**
- If 5 stdio servers are being spawned simultaneously, 6th request blocks
- All servers share same semaphore (no per-server limits)
- Could cause cascading delays

**Recommendation:** Per-server semaphores or higher global limit

---

### 🟡 **MODERATE: No Retry Logic for Transient Failures**

**Problem:**
- Single failure immediately increments circuit breaker
- No distinction between transient (network blip) vs permanent (server down) failures
- No exponential backoff or retry with jitter

**Impact:**
- Temporary network issues can disable servers for full 5 minutes
- No graceful degradation

**Recommendation:** Implement retry logic with exponential backoff before recording failure

---

### 🟢 **MINOR: Circuit Breaker State Not Persisted**

**Problem:**
- Circuit breaker state is in-memory only
- Agent-runner restart resets all circuit breakers
- No historical failure tracking

**Impact:**
- Can't learn from past failures
- Restart "fixes" circuit breakers even if servers are still broken

**Recommendation:** Persist circuit breaker state to disk (optional, low priority)

---

## Failure Scenarios Analysis

### Scenario 1: Remote Server (exa) Network Failure

**Current Behavior:**
1. 3 consecutive failures → circuit breaker opens
2. Server disabled for 5 minutes
3. Other servers (local stdio) continue working ✅
4. After 5 minutes, recovery test resets breaker
5. If still failing, breaker opens again

**Resilience:** ✅ **Good** - Isolated failure, doesn't affect other servers

---

### Scenario 2: Local Server (project-memory) Startup Failure

**Current Behavior:**
1. Process spawn fails (e.g., SurrealDB not running)
2. 3 consecutive failures → circuit breaker opens
3. Server disabled for 5 minutes
4. Other servers continue working ✅
5. Recovery test resets breaker, but server still broken → immediate re-failure

**Resilience:** 🟡 **Moderate** - Isolated but recovery doesn't work well

---

### Scenario 3: Agent-Runner Process Hung (Not Dead)

**Current Behavior:**
1. Agent-runner process alive but not responding to HTTP
2. Router detects unresponsiveness, sends notifications
3. Router can disable `mcp_tool_access_enabled` (if auto-toggle enabled)
4. **ALL local stdio servers become unavailable** ❌
5. Remote servers (exa) also unavailable (can't reach agent-runner)

**Resilience:** 🔴 **Poor** - Single point of failure affects everything

---

### Scenario 4: Internet Connectivity Lost

**Current Behavior:**
1. Remote server (exa) fails → circuit breaker opens
2. Local stdio servers continue working ✅
3. But: If agent-runner HTTP interface also affected, router may disable MCP access

**Resilience:** 🟡 **Moderate** - Local servers should work, but router may block them

---

### Scenario 5: System Resource Exhaustion (File Handles)

**Current Behavior:**
1. Too many concurrent stdio subprocesses
2. Semaphore limits to 5 concurrent
3. But: If processes don't clean up properly, handles can still leak
4. New spawns fail with "Too many open files"
5. All stdio servers fail together ❌

**Resilience:** 🟡 **Moderate** - Semaphore helps but not foolproof

---

### Scenario 6: One Local Server Continuously Failing

**Current Behavior:**
1. Server fails → circuit breaker opens (5 min)
2. Recovery test resets breaker
3. Server fails again → breaker opens again
4. Other servers continue working ✅
5. But: Recovery test doesn't actually verify server is working

**Resilience:** 🟡 **Moderate** - Isolated but inefficient recovery

---

## Local vs Remote Server Comparison

| Aspect | Local (stdio) | Remote (http/ws/sse) |
|--------|---------------|----------------------|
| **Failure Mode** | Process spawn/IO errors | Network/HTTP errors |
| **Recovery Time** | Instant (if process works) | Depends on network |
| **Dependency** | Agent-runner process | Network + remote service |
| **Isolation** | Shared agent-runner process | Independent services |
| **Circuit Breaker** | Same (3 failures, 5 min) | Same (3 failures, 5 min) |
| **Recovery Test** | Same (just resets) | Same (just resets) |
| **When Agent-Runner Hangs** | ❌ All unavailable | ❌ All unavailable |

**Key Insight:** Local and remote servers are treated identically in circuit breaker logic, which is acceptable given per-server isolation. The main difference is that local servers are spawned per-request (not persistent).

---

## Recommendations for Maximum Resilience

### Priority 1: Critical (Must Have)

1. **Persistent Local Stdio Server Management**
   - **What this means:** Currently, every time you call a local stdio MCP server (like `firecrawl-mcp` or `project-memory`), the system:
     - Spawns a new subprocess (e.g., `npx -y firecrawl-mcp`)
     - Does the initialize handshake
     - Makes the tool call
     - **Kills the process immediately** (line 1981: `proc.kill()`)
   - **Persistent management would mean:**
     - Spawn the process **once** when first needed
     - **Keep it alive** between requests
     - Reuse the same process for multiple calls
     - Only restart if the process dies or has issues
   - **Why this matters:** 
     - If agent-runner HTTP interface hangs, the persistent processes could still be accessible
     - Much faster (no spawn/init overhead per call)
     - Processes can maintain state between calls
   - **Impact:** Local servers remain available even if agent-runner HTTP interface has issues

2. **Actual Recovery Testing**
   - Before resetting circuit breaker, make actual health check call
   - Implement half-open state (test with single request)
   - Only reset if test succeeds
   - **Impact:** Servers don't get re-enabled if still broken

### Priority 2: High (Should Have)

3. **Retry Logic with Exponential Backoff**
   - Retry transient failures before recording to circuit breaker
   - Distinguish transient vs permanent failures
   - **Impact:** Temporary issues don't disable servers

4. **Independent Local Server Access**
   - Make local stdio servers accessible even if agent-runner HTTP is hung
   - Consider separate process/thread for local server management
   - **Impact:** Local servers work even when agent-runner has issues

5. **Per-Server Resource Limits**
   - Separate semaphores or higher limits per server type
   - **Impact:** One server's load doesn't block others

### Priority 3: Medium (Nice to Have)

6. **Gradual Circuit Breaker Recovery**
   - Half-open state with limited requests
   - Gradual increase in allowed requests
   - **Impact:** Smoother recovery from failures

7. **Circuit Breaker State Persistence**
   - Save state to disk
   - Restore on restart
   - **Impact:** Learn from past failures

8. **Health Check Endpoints for Local Servers**
   - Lightweight ping/test for stdio servers
   - **Impact:** Better recovery testing

---

## Current System Capabilities

### ✅ What Works Well

- **Per-server isolation** - One server's failures don't directly disable others
- **Automatic circuit breaking** - Prevents cascading failures
- **Comprehensive logging** - Good visibility into failures
- **Manual recovery** - `/admin/reload-mcp` for manual intervention
- **Health monitoring** - Background task tracks server status

### ❌ What Doesn't Work Well

- **Local server dependency** - All local servers depend on agent-runner process
- **No persistent connections** - Every call spawns new process
- **Ineffective recovery** - Recovery test doesn't verify server is actually working
- **No retry logic** - Single failure immediately counts toward circuit breaker
- **Identical treatment** - Local and remote servers managed the same way

---

## Conclusion

The current system provides **basic resilience** but has **critical architectural limitations** that prevent maximum server availability:

1. **Local stdio servers are not persistent** - They're spawned per-request and killed immediately
2. **No distinction between local and remote** - They're managed identically despite different characteristics
3. **Recovery doesn't verify actual recovery** - Circuit breakers reset without testing
4. **Single point of failure** - If agent-runner hangs, all servers become unavailable

**To achieve maximum resilience and keep as many servers available as possible:**

- **Must implement persistent local server management** (keep stdio processes alive)
- **Must implement actual recovery verification** (test before resetting circuit breaker)
- **Should add retry logic for transient failures** (don't count single failures immediately)
- **Should make local servers independent of agent-runner HTTP interface** (if HTTP hangs, processes still work)

The system is **functional but not optimal** for maximum resilience. With the recommended changes, it could achieve **9/10 resilience score**.

