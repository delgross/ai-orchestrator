# Code Improvements for Faster Problem Identification and Repair

This document outlines improvements to make debugging and problem-solving faster for both AI assistants and human developers.

## 1. Structured Error Responses (High Priority)

**Problem:** Errors are inconsistent, making it hard to identify the type and cause.

**Solution:** Standardize all error responses with error codes and categories.

```python
# Standard error response format
{
    "ok": False,
    "error": {
        "code": "MCP_SERVER_UNAVAILABLE",  # Machine-readable error code
        "category": "mcp_connection",      # Error category
        "message": "MCP server 'project-memory' is not responding",
        "details": {
            "server": "project-memory",
            "timeout": 15.0,
            "last_success": "2025-01-17T10:30:00Z"
        },
        "suggestions": [
            "Check if SurrealDB is running",
            "Verify MCP server configuration",
            "Review agent-runner logs for connection errors"
        ],
        "request_id": "abc123",
        "timestamp": "2025-01-17T10:35:00Z"
    }
}
```

**Error Categories:**
- `mcp_connection` - MCP server connection issues
- `mcp_tool_call` - Tool execution failures
- `memory_error` - Database/memory issues
- `gateway_error` - Router/gateway problems
- `validation_error` - Input validation failures
- `config_error` - Configuration problems
- `timeout` - Timeout errors
- `unknown` - Unclassified errors

**Implementation:**
```python
class ErrorCode(Enum):
    MCP_SERVER_UNAVAILABLE = "MCP_SERVER_UNAVAILABLE"
    MCP_TOOL_CALL_FAILED = "MCP_TOOL_CALL_FAILED"
    MEMORY_CONNECTION_FAILED = "MEMORY_CONNECTION_FAILED"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"
    # ... more codes

def create_error_response(
    code: ErrorCode,
    category: str,
    message: str,
    details: Optional[Dict] = None,
    suggestions: Optional[List[str]] = None
) -> Dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "code": code.value,
            "category": category,
            "message": message,
            "details": details or {},
            "suggestions": suggestions or [],
            "request_id": request_id_var.get(''),
            "timestamp": datetime.now().isoformat()
        }
    }
```

## 2. Comprehensive Health Check Endpoint (High Priority)

**Problem:** No single endpoint to check all system components.

**Solution:** Create `/admin/health` that checks all subsystems.

```python
@app.get("/admin/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check of all system components."""
    health = {
        "status": "healthy",  # healthy, degraded, unhealthy
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Check MCP servers
    mcp_health = {}
    for server in MCP_SERVERS.keys():
        try:
            res = await tool_mcp_proxy(server=server, tool="check_health", arguments={})
            mcp_health[server] = {
                "status": "healthy" if res.get("ok") else "unhealthy",
                "details": res
            }
        except Exception as e:
            mcp_health[server] = {
                "status": "unhealthy",
                "error": str(e)
            }
    health["components"]["mcp_servers"] = mcp_health
    
    # Check gateway/router
    try:
        resp = await _http_client.get(f"{GATEWAY_BASE}/health", timeout=5.0)
        health["components"]["gateway"] = {
            "status": "healthy" if resp.status_code == 200 else "degraded",
            "status_code": resp.status_code
        }
    except Exception as e:
        health["components"]["gateway"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check memory/database
    try:
        res = await tool_mcp_proxy(server="project-memory", tool="check_health", arguments={})
        health["components"]["memory"] = {
            "status": "healthy" if res.get("ok") else "unhealthy",
            "details": res
        }
    except Exception as e:
        health["components"]["memory"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Determine overall status
    all_healthy = all(
        comp.get("status") == "healthy" 
        for comp in health["components"].values()
    )
    any_unhealthy = any(
        comp.get("status") == "unhealthy"
        for comp in health["components"].values()
    )
    
    if any_unhealthy:
        health["status"] = "unhealthy"
    elif not all_healthy:
        health["status"] = "degraded"
    
    return health
```

## 3. Enhanced Logging with Context (High Priority)

**Problem:** Logs lack context, making it hard to trace issues.

**Solution:** Add structured logging with consistent context.

```python
# Enhanced logging helper
def log_with_context(
    level: str,
    message: str,
    component: str,
    **kwargs
):
    """Log with consistent context structure."""
    context = {
        "request_id": request_id_var.get(''),
        "component": component,
        "agent_model": get_agent_model(),
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }
    
    log_func = getattr(logger, level.lower())
    log_func(message, extra=context)
    
    # Also log as JSON event for parsing
    _log_json_event(
        f"{component}_{level.lower()}",
        message=message,
        **context
    )

# Usage:
log_with_context(
    "error",
    "MCP server connection failed",
    component="mcp_client",
    server="project-memory",
    timeout=15.0,
    error=str(e)
)
```

## 4. Diagnostic Endpoints (Medium Priority)

**Problem:** Hard to inspect internal state when debugging.

**Solution:** Add diagnostic endpoints that expose internal state.

```python
@app.get("/admin/diagnostics")
async def diagnostics() -> Dict[str, Any]:
    """Diagnostic information for debugging."""
    return {
        "system": {
            "agent_model": get_agent_model(),
            "fallback_model": _FALLBACK_MODEL,
            "fallback_enabled": _FALLBACK_ENABLED,
            "mcp_tool_access_enabled": state.mcp_tool_access_enabled,
            "active_model": state.active_model,
        },
        "mcp_servers": {
            server: {
                "configured": True,
                "tools_count": len([t for t in MCP_TOOLS if t.get("function", {}).get("name", "").startswith(f"mcp__{server}__")]),
                "circuit_breaker": _mcp_circuit_breaker.get(server, {}),
            }
            for server in MCP_SERVERS.keys()
        },
        "memory": {
            "tool_available": "mcp__project_memory__query_facts" in TOOL_IMPLS,
            "recent_health": await _get_memory_health_status(),
        },
        "metrics": {
            "total_tool_calls": _tool_metrics.get("total", {}).get("calls", 0),
            "success_rate": _calculate_success_rate(),
        }
    }

@app.get("/admin/diagnostics/mcp/{server}")
async def mcp_diagnostics(server: str) -> Dict[str, Any]:
    """Detailed diagnostics for a specific MCP server."""
    if server not in MCP_SERVERS:
        raise HTTPException(404, detail=f"MCP server '{server}' not found")
    
    return {
        "server": server,
        "config": MCP_SERVERS[server],
        "tools": [
            {
                "name": t.get("function", {}).get("name"),
                "description": t.get("function", {}).get("description", "")[:100],
            }
            for t in MCP_TOOLS
            if t.get("function", {}).get("name", "").startswith(f"mcp__{server}__")
        ],
        "circuit_breaker": _mcp_circuit_breaker.get(server, {}),
        "health_check": await _test_mcp_health(server),
    }
```

## 5. Input Validation with Clear Errors (Medium Priority)

**Problem:** Validation errors are unclear.

**Solution:** Validate early with descriptive error messages.

```python
def validate_mcp_proxy_request(body: Dict[str, Any]) -> Tuple[str, str, Dict]:
    """Validate MCP proxy request and return (server, tool, arguments) or raise."""
    server = body.get("server")
    if not server:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                ErrorCode.VALIDATION_ERROR,
                "validation_error",
                "Missing required field: 'server'",
                suggestions=["Include 'server' field in request body"]
            )
        )
    
    if server not in MCP_SERVERS:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(
                ErrorCode.MCP_SERVER_NOT_FOUND,
                "validation_error",
                f"MCP server '{server}' not found",
                details={"available_servers": list(MCP_SERVERS.keys())},
                suggestions=[f"Use one of: {', '.join(MCP_SERVERS.keys())}"]
            )
        )
    
    tool = body.get("tool")
    if not tool:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                ErrorCode.VALIDATION_ERROR,
                "validation_error",
                "Missing required field: 'tool'",
                suggestions=["Include 'tool' field in request body"]
            )
        )
    
    return server, tool, body.get("arguments", {})
```

## 6. Error Recovery Suggestions (Medium Priority)

**Problem:** Errors don't suggest how to fix them.

**Solution:** Include actionable suggestions in error responses.

```python
def get_error_suggestions(error_code: ErrorCode, context: Dict) -> List[str]:
    """Get actionable suggestions based on error code and context."""
    suggestions_map = {
        ErrorCode.MCP_SERVER_UNAVAILABLE: [
            f"Check if {context.get('server')} MCP server is running",
            "Verify MCP server configuration in config.yaml",
            "Check agent-runner logs for connection errors",
            "Try restarting the agent-runner service",
        ],
        ErrorCode.MEMORY_CONNECTION_FAILED: [
            "Verify SurrealDB is running: `curl http://127.0.0.1:8000/health`",
            "Check SURREAL_URL, SURREAL_USER, SURREAL_PASS environment variables",
            "Review memory_server.py logs for connection errors",
            "Test connection: `./manage.sh restart agent`",
        ],
        ErrorCode.GATEWAY_TIMEOUT: [
            "Check router/gateway service status",
            "Verify GATEWAY_BASE configuration",
            "Check network connectivity",
            "Review gateway logs for errors",
        ],
    }
    return suggestions_map.get(error_code, ["Check logs for more details"])
```

## 7. Type Hints and Documentation (Low Priority)

**Problem:** Unclear function signatures make it hard to understand what can go wrong.

**Solution:** Add comprehensive type hints and docstrings.

```python
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

class ErrorCode(Enum):
    """Error codes for structured error responses."""
    MCP_SERVER_UNAVAILABLE = "MCP_SERVER_UNAVAILABLE"
    # ...

async def tool_mcp_proxy(
    server: str,
    tool: str,
    arguments: Dict[str, Any],
    timeout: float = 30.0
) -> Dict[str, Any]:
    """
    Call an MCP tool via proxy.
    
    Args:
        server: MCP server name (must be in MCP_SERVERS)
        tool: Tool name (without 'mcp__{server}__' prefix)
        arguments: Tool arguments
        timeout: Request timeout in seconds
        
    Returns:
        Dict with 'ok' key indicating success/failure
        
    Raises:
        ValueError: If server not found
        TimeoutError: If request times out
        ConnectionError: If MCP server unavailable
        
    Example:
        >>> result = await tool_mcp_proxy("project-memory", "query_facts", {})
        >>> if result.get("ok"):
        ...     facts = result.get("facts", [])
    """
    # Implementation...
```

## 8. Dashboard Error Display (Medium Priority)

**Problem:** Dashboard doesn't show structured error information.

**Solution:** Display error codes, categories, and suggestions in dashboard.

```javascript
function displayError(error) {
    if (error.error && error.error.code) {
        // Structured error
        const code = error.error.code;
        const category = error.error.category;
        const message = error.error.message;
        const suggestions = error.error.suggestions || [];
        
        return `
            <div class="error-display">
                <div class="error-code">${code}</div>
                <div class="error-category">${category}</div>
                <div class="error-message">${message}</div>
                ${suggestions.length > 0 ? `
                    <div class="error-suggestions">
                        <strong>Suggestions:</strong>
                        <ul>
                            ${suggestions.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    } else {
        // Fallback for unstructured errors
        return `<div class="error-display">${error.error || error.message || 'Unknown error'}</div>`;
    }
}
```

## 9. Automated Health Monitoring (Low Priority)

**Problem:** Problems aren't detected until user reports them.

**Solution:** Add background health monitoring with alerts.

```python
async def _health_monitor_task():
    """Background task to monitor system health."""
    health = await health_check()
    
    if health["status"] == "unhealthy":
        # Log critical health issue
        log_with_context(
            "error",
            "System health check failed",
            component="health_monitor",
            health_status=health["status"],
            unhealthy_components=[
                name for name, comp in health["components"].items()
                if comp.get("status") == "unhealthy"
            ]
        )
        
        # Could also send alerts, update metrics, etc.
```

## Implementation Priority

1. **High Priority:**
   - Structured error responses with error codes
   - Comprehensive health check endpoint
   - Enhanced logging with context

2. **Medium Priority:**
   - Diagnostic endpoints
   - Input validation with clear errors
   - Error recovery suggestions
   - Dashboard error display

3. **Low Priority:**
   - Type hints and documentation
   - Automated health monitoring

## Benefits

- **Faster Problem Identification:** Error codes and categories make it immediately clear what's wrong
- **Better Debugging:** Diagnostic endpoints expose internal state
- **Actionable Errors:** Suggestions tell users how to fix problems
- **Consistent Structure:** Standardized formats make parsing and handling easier
- **Better Observability:** Enhanced logging provides full context







