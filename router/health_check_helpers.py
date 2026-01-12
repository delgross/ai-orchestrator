"""
Helper functions for health checks.
Extracts duplicate health check logic.
"""
import logging
import os
from pathlib import Path
from typing import Optional, Any
import httpx

logger = logging.getLogger(__name__)

async def check_service_health(
    service_name: str,
    url: str,
    circuit_breaker: Any,
    http_client: httpx.AsyncClient,
    timeout: float = 2.0
) -> bool:
    """
    Check health of a service and update circuit breaker.
    
    Args:
        service_name: Name of the service (e.g., "ollama", "agent_runner")
        url: Health check URL
        circuit_breaker: Circuit breaker registry
        http_client: HTTP client to use
        timeout: Request timeout in seconds
        
    Returns:
        True if service is healthy, False otherwise
    """
    try:
        if circuit_breaker.is_allowed(service_name):
            r = await http_client.get(url, timeout=timeout)
            if r.status_code == 200:
                circuit_breaker.record_success(service_name)
                return True
            else:
                circuit_breaker.record_failure(service_name, error=f"HTTP {r.status_code}")
                return False
    except Exception as e:
        circuit_breaker.record_failure(service_name, error=str(e))
        logger.debug(f"Watchdog: {service_name} check failed: {e}")
        return False


def check_cache_freshness(project_root: Optional[str] = None) -> tuple[bool, list[str]]:
    """
    Check if Python bytecode cache is fresh (no stale .pyc files).

    Returns:
        tuple: (is_fresh: bool, stale_files: list[str])
    """
    if project_root is None:
        # Try to find project root
        current = Path.cwd()
        while current.parent != current:
            if (current / "manage.sh").exists():
                project_root = str(current)
                break
            current = current.parent

    if project_root is None:
        project_root = str(Path.cwd())

    root_path = Path(project_root)
    stale_files = []

    try:
        # Check all .py files for stale .pyc counterparts
        for py_file in root_path.rglob("*.py"):
            pyc_file = py_file.with_suffix('.pyc')
            if pyc_file.exists():
                try:
                    py_mtime = py_file.stat().st_mtime
                    pyc_mtime = pyc_file.stat().st_mtime
                    if pyc_mtime > py_mtime:
                        stale_files.append(str(py_file.relative_to(root_path)))
                except OSError:
                    # Skip files we can't stat
                    continue

        is_fresh = len(stale_files) == 0

        if not is_fresh:
            logger.warning(f"⚠️ Found {len(stale_files)} potentially stale bytecode files")
            for stale_file in stale_files[:5]:  # Log first 5
                logger.debug(f"Stale: {stale_file}")

        return is_fresh, stale_files

    except Exception as e:
        logger.error(f"Cache freshness check failed: {e}")
        return False, ["check_failed"]

