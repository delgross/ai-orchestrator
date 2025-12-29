import logging
from typing import Dict, Any, List
from router.config import state, AGENT_RUNNER_URL

logger = logging.getLogger("router.agent_manager")

async def check_agent_runner_health() -> bool:
    if not state.circuit_breakers.is_allowed("agent-runner"):
        return False

    try:
        r = await state.client.get(f"{AGENT_RUNNER_URL}/", timeout=3.0)
        if r.status_code < 400:
            data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            ok = data.get("ok", False)
            if ok:
                state.circuit_breakers.record_success("agent-runner")
            else:
                state.circuit_breakers.record_failure("agent-runner")
            return ok
        state.circuit_breakers.record_failure("agent-runner")
        return False
    except Exception as e:
        state.circuit_breakers.record_failure("agent-runner")
        logger.error(f"Agent-runner health check failed: {e}")
        return False

async def get_agent_models() -> List[Dict[str, Any]]:
    if not state.circuit_breakers.is_allowed("agent-runner"):
        return []

    try:
        r = await state.client.get(f"{AGENT_RUNNER_URL}/v1/models", timeout=5.0)
        if r.status_code == 200:
            state.circuit_breakers.record_success("agent-runner")
            return r.json().get("data", [])
        state.circuit_breakers.record_failure("agent-runner")
    except Exception as e:
        state.circuit_breakers.record_failure("agent-runner")
        logger.debug(f"Failed to fetch agent models: {e}")
    return []
