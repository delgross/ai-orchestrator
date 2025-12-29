import logging
from typing import Dict, Any, Optional
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner")

def record_mcp_failure(state: AgentState, server: str, error_context: Optional[Dict[str, Any]] = None) -> None:
    """
    Record an MCP server failure using the centralized CircuitBreakerRegistry.
    Refactored to support the new Registry object instead of a dict.
    """
    try:
        # Pass weight=1 by default, but we could use error_context to determine severity
        state.mcp_circuit_breaker.record_failure(server)
    except Exception as e:
        logger.error(f"Error in record_mcp_failure wrapper: {e}")

def reset_mcp_success(state: AgentState, server: str) -> None:
    """
    Reset or record success for circuit breaker on successful call.
    Refactored to support the new Registry object.
    """
    try:
        state.mcp_circuit_breaker.record_success(server)
    except Exception as e:
        logger.error(f"Error in reset_mcp_success wrapper: {e}")
