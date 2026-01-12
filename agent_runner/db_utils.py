"""
Surreal query helper to centralize DB access and SurrealQL safety.
All Surreal queries should go through `run_query` to ensure consistent headers,
validation, retries, and logging handled by MemoryServer._execute_query.
"""
from typing import Any, Dict, Optional


async def run_query(state: Any, query: str, params: Optional[Dict[str, Any]] = None, raise_on_error: bool = False, **kwargs) -> Any:
    """
    Execute a Surreal query via state's memory server helper.
    Enforces that memory is available and delegates to MemoryServer._execute_query,
    which applies SurrealQL safety checks (no SQL patterns, NS/DB prefixes, retries, logging).
    """
    if not state or not getattr(state, "memory", None):
        raise RuntimeError("Memory server not available on state.")
    return await state.memory.execute_query(query, params=params, raise_on_error=raise_on_error, **kwargs)


async def run_query_with_memory(memory: Any, query: str, params: Optional[Dict[str, Any]] = None, raise_on_error: bool = False, **kwargs) -> Any:
    """
    Execute a Surreal query when only a MemoryServer-like object is available.
    This is a thin wrapper to avoid signature churn where state is not passed through.
    """
    if not memory:
        raise RuntimeError("Memory server not available.")
    return await memory.execute_query(query, params=params, raise_on_error=raise_on_error, **kwargs)

