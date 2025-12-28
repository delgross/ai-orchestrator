"""
Error handling utilities for consistent error processing and structured responses.

Combines:
- Exception message extraction with blank message detection (from router)
- Structured error responses with actionable suggestions (from agent-runner)
"""

from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("error_utils")


class ErrorCode(Enum):
    """Error codes for structured error responses."""
    MCP_SERVER_UNAVAILABLE = "MCP_SERVER_UNAVAILABLE"
    MCP_SERVER_NOT_FOUND = "MCP_SERVER_NOT_FOUND"
    MCP_TOOL_CALL_FAILED = "MCP_TOOL_CALL_FAILED"
    MCP_TOOL_NOT_FOUND = "MCP_TOOL_NOT_FOUND"
    MEMORY_CONNECTION_FAILED = "MEMORY_CONNECTION_FAILED"
    MEMORY_QUERY_FAILED = "MEMORY_QUERY_FAILED"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"
    GATEWAY_ERROR = "GATEWAY_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CONFIG_ERROR = "CONFIG_ERROR"
    TIMEOUT = "TIMEOUT"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    ROUTER_ERROR = "ROUTER_ERROR"
    AGENT_RUNNER_ERROR = "AGENT_RUNNER_ERROR"


def get_error_message(e: Exception, context: str = "unknown") -> str:
    """
    Get error message from exception, detecting and logging blank messages.
    
    Blank error messages are themselves an error condition that should be detected
    and logged, as they indicate a problem with exception handling or the exception itself.
    
    Args:
        e: The exception
        context: Context where error occurred (for logging)
    
    Returns:
        Non-empty error message (guaranteed)
    """
    error_str = str(e)
    error_type = type(e).__name__
    
    # Detect blank error messages - this is itself an error condition
    if not error_str or error_str.strip() == "":
        logger.error(
            "BLANK ERROR MESSAGE DETECTED",
            extra={
                "error_type": error_type,
                "exception_repr": repr(e),
                "exception_args": str(e.args) if hasattr(e, 'args') and e.args else None,
                "context": context,
                "location": context
            }
        )
    
    # Return non-empty message with fallbacks
    return error_str or error_type or "Unknown error"


def create_error_response(
    code: ErrorCode,
    category: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    suggestions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a structured error response.
    
    Args:
        code: Error code enum
        category: Error category (e.g., "mcp_connection", "memory_error")
        message: Human-readable error message
        details: Additional error details
        suggestions: List of actionable suggestions to fix the error
        
    Returns:
        Structured error response dict
    """
    return {
        "ok": False,
        "error": {
            "code": code.value,
            "category": category,
            "message": message,
            "details": details or {},
            "suggestions": suggestions or [],
            "timestamp": datetime.now().isoformat()
        }
    }


def get_error_suggestions(error_code: ErrorCode, context: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Get actionable suggestions based on error code and context.
    
    Args:
        error_code: The error code
        context: Optional context dict with additional info (e.g., {"server": "project-memory"})
        
    Returns:
        List of suggestion strings
    """
    context = context or {}
    suggestions_map = {
        ErrorCode.MCP_SERVER_UNAVAILABLE: [
            f"Check if {context.get('server', 'the')} MCP server is running",
            "Verify MCP server configuration in config.yaml",
            "Check agent-runner logs for connection errors",
            "Try restarting the agent-runner service: `./manage.sh restart agent`",
        ],
        ErrorCode.MCP_SERVER_NOT_FOUND: [
            f"Verify '{context.get('server', 'server')}' is configured in config.yaml",
            f"Check available servers: {context.get('available_servers', 'see config.yaml')}",
            "Ensure MCP server name matches exactly (case-sensitive)",
        ],
        ErrorCode.MCP_TOOL_CALL_FAILED: [
            f"Verify tool '{context.get('tool', 'tool')}' exists for server '{context.get('server', 'server')}'",
            "Check MCP server logs for tool execution errors",
            "Verify tool arguments are correct",
            "Try calling the tool directly via /admin/mcp/proxy endpoint",
        ],
        ErrorCode.MEMORY_CONNECTION_FAILED: [
            "Verify SurrealDB is running: `curl http://127.0.0.1:8000/health`",
            "Check SURREAL_URL, SURREAL_USER, SURREAL_PASS environment variables in config.yaml",
            "Review memory_server.py logs for connection errors",
            "Test connection: `./manage.sh restart agent`",
        ],
        ErrorCode.MEMORY_QUERY_FAILED: [
            "Check if SurrealDB connection is healthy",
            "Verify database schema is initialized",
            "Check memory server logs for query errors",
        ],
        ErrorCode.GATEWAY_TIMEOUT: [
            "Check router/gateway service status",
            "Verify GATEWAY_BASE configuration",
            "Check network connectivity",
            "Review gateway logs for errors",
        ],
        ErrorCode.GATEWAY_ERROR: [
            "Check router/gateway service is running",
            "Verify GATEWAY_BASE URL is correct",
            "Check gateway logs for detailed error information",
        ],
        ErrorCode.VALIDATION_ERROR: [
            "Verify all required fields are present in the request",
            "Check field types match expected format",
            "Review API documentation for correct request format",
        ],
        ErrorCode.CONFIG_ERROR: [
            "Verify config.yaml syntax is valid YAML",
            "Check all required configuration fields are present",
            "Review config.yaml.example for correct format",
        ],
        ErrorCode.AUTH_ERROR: [
            "Verify authentication token is correct",
            "Check if token has expired",
            "Review authentication configuration",
        ],
        ErrorCode.ROUTER_ERROR: [
            "Check router service status",
            "Review router logs for detailed error information",
            "Verify router configuration is correct",
        ],
        ErrorCode.AGENT_RUNNER_ERROR: [
            "Check agent-runner service status",
            "Review agent-runner logs for detailed error information",
            "Verify agent-runner configuration is correct",
        ],
    }
    return suggestions_map.get(error_code, ["Check logs for more details", "Review error details for specific information"])





