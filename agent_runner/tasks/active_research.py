
import logging
from agent_runner.agent_runner import get_shared_state

logger = logging.getLogger("agent_runner.tasks.active_research")

async def active_research_task():
    """
    Background process that researches 'active_research' topics.
    Tempo gating is handled by the Scheduler, so this function only runs
    when we are already in the correct state (REFLECTIVE+).
    """
    state = get_shared_state()
    logger.info("Starting Active Research Cycle (Tempo Confirmed via Scheduler)...")
    
    # Logic: Mock Implementation for Phase 12 verification
    from agent_runner.tools.mcp import tool_mcp_proxy
    try:
        # Check 'active_research' bank
        res = await tool_mcp_proxy(state, "project-memory", "list_memory_banks", {}, bypass_circuit_breaker=True)
        if res.get("ok"):
            banks = res.get("result", {}).get("banks", [])
            research_bank = next((b for b in banks if b["kb_id"] == "active_research"), None)
            
            if research_bank:
                count = research_bank.get("fact_count", 0)
                logger.info(f"Found {count} items in 'active_research'. Analysing...")
                # Future: Pick item, search Tavily, Store result.
            else:
                logger.info("'active_research' bank is empty or missing. No dreaming today.")
                
    except Exception as e:
        logger.warning(f"Active Research probe failed: {e}")
