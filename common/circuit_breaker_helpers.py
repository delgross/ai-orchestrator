"""
Helper functions for circuit breaker checks.
Extracts duplicate patterns to reduce code duplication.
"""
import logging
from typing import Optional, Dict, Any
from common.circuit_breaker import CircuitBreakerRegistry

logger = logging.getLogger(__name__)

def check_circuit_breaker(
    circuit_breaker: CircuitBreakerRegistry,
    server: str
) -> Optional[Dict[str, Any]]:
    """
    Check circuit breaker, return error dict if open.
    
    Args:
        circuit_breaker: The circuit breaker registry to check
        server: The server name to check
        
    Returns:
        Error dict if circuit breaker is open, None otherwise
    """
    if not circuit_breaker.is_allowed(server):
        logger.warning(f"Server '{server}' is circuit broken")
        return {"ok": False, "error": "Circuit breaker active"}
    return None

