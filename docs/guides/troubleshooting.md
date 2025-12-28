# Troubleshooting with Diagnostic Data

## Overview

The system generates rich diagnostic data that can be used for intelligent troubleshooting. This document explains how to leverage this data when debugging issues.

## Available Diagnostic Endpoints

### 1. Circuit Breaker Status
**Endpoint:** `GET /admin/circuit-breaker/status`

**What it tells us:**
- Which servers are disabled and why
- Failure counts for each server
- Time until recovery
- Half-open state testing

**Use cases:**
- Identify which servers are failing
- Understand failure patterns (single server vs. system-wide)
- Determine if failures are transient or persistent

**Example:**
```bash
curl http://127.0.0.1:5460/admin/circuit-breaker/status | jq
```

### 2. System Diagnostics
**Endpoint:** `GET /admin/diagnostics`

**What it tells us:**
- System configuration
- MCP server configuration status
- Tool availability
- Memory server health

**Use cases:**
- Verify system configuration
- Check if tools are properly registered
- Identify missing or misconfigured servers

### 3. MCP Server Diagnostics
**Endpoint:** `GET /admin/diagnostics/mcp/{server}`

**What it tells us:**
- Server configuration details
- Available tools for that server
- Health check results
- Transport type (stdio/http/ws/unix)

**Use cases:**
- Deep dive into specific server issues
- Verify server configuration
- Check tool availability

### 4. Stdio Process Status
**Endpoint:** `GET /admin/mcp/stdio/status`

**What it tells us:**
- Which stdio processes are running
- Process initialization status
- Process health timestamps
- Process PIDs

**Use cases:**
- Debug stdio server initialization issues
- Identify dead or stuck processes
- Verify process lifecycle

### 5. Health Check
**Endpoint:** `GET /admin/health`

**What it tells us:**
- Overall system health
- Component-by-component status
- Gateway connectivity
- Memory database status
- Task server status

**Use cases:**
- Get comprehensive system overview
- Identify unhealthy components
- Check system-wide issues

### 6. Memory Server Status
**Endpoint:** `GET /admin/memory`

**What it tells us:**
- Memory server health
- Database connectivity
- Recent facts
- Query capability

**Use cases:**
- Debug memory/database issues
- Verify facts are being stored
- Check database connectivity

## State Snapshots in Logs

When circuit breakers trigger, state snapshots are logged with:
- **Circuit breaker state**: Current failures, disabled_until, state
- **Server configuration**: Transport type, URL, environment variables
- **Process state** (for stdio): Alive/dead, PID, returncode, initialized status
- **Other circuit breakers**: State of all other servers (for correlation)
- **Error context**: Specific error, transport type, retry attempt

**How to use:**
1. Search logs for `mcp_server_disabled` events
2. Extract `state_snapshot` from log entries
3. Analyze patterns:
   - Multiple stdio servers failing → agent-runner issue
   - All HTTP servers failing → network issue
   - Single server failing → server-specific issue

## Intelligent Troubleshooting Workflow

### Step 1: Check Circuit Breaker Status
```bash
curl http://127.0.0.1:5460/admin/circuit-breaker/status | jq '.circuit_breakers | to_entries | map(select(.value.is_blocked))'
```

**Analysis:**
- If multiple servers disabled → system-wide issue
- If only stdio servers → agent-runner or process management issue
- If only HTTP/WS servers → network connectivity issue
- If single server → server-specific configuration or service issue

### Step 2: Check Process Status (for stdio servers)
```bash
curl http://127.0.0.1:5460/admin/mcp/stdio/status | jq '.processes[] | select(.server == "project-memory")'
```

**Analysis:**
- `running: false` → Process not created or died
- `initialized: false` → Initialization handshake failed
- `last_health: 0` → Process never healthy
- `returncode: -1` → Process died with error

### Step 3: Check Server-Specific Diagnostics
```bash
curl http://127.0.0.1:5460/admin/diagnostics/mcp/project-memory | jq
```

**Analysis:**
- Check `health_check.status` → Is server responding?
- Check `tools` → Are tools properly registered?
- Check `config.scheme` → Is transport type correct?

### Step 4: Analyze State Snapshots from Logs
```bash
grep "mcp_server_disabled" ~/Library/Logs/ai/agent_runner.err.log | jq -r '.state_snapshot' | jq
```

**Analysis:**
- `stdio_process.exists: false` → Process creation failed
- `stdio_process.alive: false` → Process died
- `stdio_process.returncode: 1` → Process exited with error
- `other_circuit_breakers` → Check for correlated failures

### Step 5: Check System Health
```bash
curl http://127.0.0.1:5460/admin/health | jq '.components'
```

**Analysis:**
- `gateway.status: unhealthy` → Router/gateway issue
- `memory.status: unhealthy` → Database connectivity issue
- `task_server.status: unhealthy` → Background task issue

## Common Troubleshooting Patterns

### Pattern 1: All Stdio Servers Failing
**Symptoms:**
- Multiple stdio servers have circuit breakers open
- State snapshots show `stdio_process.exists: false` or `alive: false`

**Likely Causes:**
- Agent-runner process issues
- System resource exhaustion (file handles, memory)
- Subprocess creation failures

**Actions:**
1. Check agent-runner logs for subprocess errors
2. Check system resources: `ulimit -n`, `ps aux | grep python`
3. Check stdio process status endpoint
4. Restart agent-runner if needed

### Pattern 2: Single Server Failing
**Symptoms:**
- One server has circuit breaker open
- Other servers working fine

**Likely Causes:**
- Server-specific configuration issue
- Service not running (for remote servers)
- Network connectivity (for HTTP/WS servers)
- Process initialization failure (for stdio)

**Actions:**
1. Check server-specific diagnostics
2. Verify server configuration
3. Check if service is running (for remote)
4. Review state snapshot for specific error

### Pattern 3: Correlated Failures
**Symptoms:**
- Multiple servers failing at similar times
- State snapshots show other circuit breakers also open

**Likely Causes:**
- Network outage (for remote servers)
- Agent-runner process hang (for stdio)
- System resource exhaustion
- Gateway/router issues

**Actions:**
1. Check system health endpoint
2. Check gateway connectivity
3. Review system resources
4. Check for system-wide events

### Pattern 4: Initialization Failures
**Symptoms:**
- Circuit breaker opens quickly
- State snapshots show `stdio_process.initialized: false`
- Process exists but not initialized

**Likely Causes:**
- MCP handshake timeout
- Process startup errors
- Environment variable issues
- Missing dependencies

**Actions:**
1. Check stdio process status
2. Review process stderr output
3. Verify environment variables
4. Test process manually

## Automated Troubleshooting Script

Here's a script that uses all diagnostic endpoints:

```python
#!/usr/bin/env python3
"""Intelligent troubleshooting using diagnostic data."""

import json
import requests
from typing import Dict, List, Any

AGENT_BASE = "http://127.0.0.1:5460"

def get_circuit_breaker_status() -> Dict[str, Any]:
    """Get circuit breaker status."""
    resp = requests.get(f"{AGENT_BASE}/admin/circuit-breaker/status")
    return resp.json()

def get_stdio_status() -> Dict[str, Any]:
    """Get stdio process status."""
    resp = requests.get(f"{AGENT_BASE}/admin/mcp/stdio/status")
    return resp.json()

def get_health() -> Dict[str, Any]:
    """Get system health."""
    resp = requests.get(f"{AGENT_BASE}/admin/health")
    return resp.json()

def get_diagnostics() -> Dict[str, Any]:
    """Get system diagnostics."""
    resp = requests.get(f"{AGENT_BASE}/admin/diagnostics")
    return resp.json()

def analyze_issues() -> List[str]:
    """Analyze diagnostic data and return issue recommendations."""
    issues = []
    
    # Check circuit breakers
    cb_status = get_circuit_breaker_status()
    disabled = [
        (name, info) 
        for name, info in cb_status.get("circuit_breakers", {}).items()
        if info.get("is_blocked", False)
    ]
    
    if disabled:
        issues.append(f"⚠️ {len(disabled)} server(s) disabled by circuit breaker:")
        for name, info in disabled:
            issues.append(f"  - {name}: {info.get('message', 'Unknown')}")
        
        # Check for patterns
        stdio_disabled = [n for n, _ in disabled if n in get_stdio_status().get("processes", {}).keys()]
        if len(stdio_disabled) == len(disabled):
            issues.append("  → All disabled servers are stdio - likely agent-runner issue")
        elif len(stdio_disabled) > 0:
            issues.append(f"  → {len(stdio_disabled)} stdio server(s) disabled - check process management")
    
    # Check system health
    health = get_health()
    unhealthy = [
        (name, comp) 
        for name, comp in health.get("components", {}).items()
        if comp.get("status") == "unhealthy"
    ]
    
    if unhealthy:
        issues.append(f"\n🔴 {len(unhealthy)} component(s) unhealthy:")
        for name, comp in unhealthy:
            error = comp.get("error", "Unknown error")
            issues.append(f"  - {name}: {error}")
    
    return issues

if __name__ == "__main__":
    print("🔍 Troubleshooting Analysis\n")
    issues = analyze_issues()
    if issues:
        print("\n".join(issues))
    else:
        print("✅ No issues detected")
```

## Using Diagnostic Data in AI Assistant

When you report an issue, I can:

1. **Query circuit breaker status** to see which servers are failing
2. **Check process status** to identify stdio initialization issues
3. **Review state snapshots** from logs to understand failure context
4. **Analyze patterns** to identify root causes (system-wide vs. isolated)
5. **Provide specific fixes** based on the diagnostic data

**Example:**
- You: "The memory server isn't working"
- Me: *Queries `/admin/circuit-breaker/status`* → "I see `project-memory` has circuit breaker open with 4 failures. Let me check the process status..."
- Me: *Queries `/admin/mcp/stdio/status`* → "The stdio process exists but isn't initialized. This suggests the MCP handshake is failing. Based on the state snapshot, the process returncode is None (alive) but initialization failed. This is likely a timing/race condition issue."

## Benefits

1. **Faster diagnosis** - Rich context available immediately
2. **Pattern recognition** - Can identify correlated failures
3. **Root cause analysis** - State snapshots show exact failure conditions
4. **Proactive detection** - Can identify issues before they become critical
5. **Targeted fixes** - Specific recommendations based on actual state



