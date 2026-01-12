"""
Automatic Tool Maintenance Tasks

Periodic tasks for tool evaluation, deprecation, and optimization.
"""

import logging
from typing import Dict, Any
from agent_runner.tools.tool_evaluation import tool_evaluate_tool_health, tool_deprecate_tool, tool_get_tool_health_dashboard
from agent_runner.agent_runner import get_shared_state

logger = logging.getLogger("agent_runner.tasks.tool_maintenance")


async def tool_evaluation_task() -> Dict[str, Any]:
    """
    Periodic task to evaluate all tools and automatically deprecate low-rated ones.
    
    Runs every 6 hours to:
    1. Evaluate all tools and calculate ratings
    2. Identify tools below threshold (rating < 0.3)
    3. Auto-deprecate tools that have been consistently failing
    4. Log findings for review
    """
    try:
        state = get_shared_state()
        logger.info("Starting automatic tool evaluation task...")
        
        # 1. Evaluate all tools
        evaluation_result = await tool_evaluate_tool_health(state, tool_name=None)
        
        if not evaluation_result.get("ok"):
            logger.error(f"Tool evaluation failed: {evaluation_result.get('error')}")
            return {"ok": False, "error": evaluation_result.get("error")}
        
        ratings = evaluation_result.get("ratings", [])
        logger.info(f"Evaluated {len(ratings)} tools")
        
        # 2. Get health dashboard to identify failing tools
        dashboard = await tool_get_tool_health_dashboard(state)
        
        if not dashboard.get("ok"):
            logger.error(f"Failed to get tool health dashboard: {dashboard.get('error')}")
            return {"ok": False, "error": dashboard.get("error")}
        
        # 3. Auto-deprecate tools with very low ratings (< 0.3) and sufficient usage (> 10 attempts)
        deprecated_count = 0
        deprecation_threshold = 0.3
        min_usage_for_deprecation = 10
        
        failing_tools = dashboard.get("failing", [])
        for tool_info in failing_tools:
            tool_name = tool_info.get("tool")
            rating = tool_info.get("rating", 1.0)
            usage_count = tool_info.get("usage_count", 0)
            
            # Only deprecate if:
            # - Rating is below threshold
            # - Has been used enough times to be statistically significant
            # - Not already deprecated
            if rating < deprecation_threshold and usage_count >= min_usage_for_deprecation:
                reason = f"Auto-deprecated: Rating {rating:.2f} below threshold {deprecation_threshold} after {usage_count} uses"
                deprecate_result = await tool_deprecate_tool(state, tool_name, reason)
                
                if deprecate_result.get("ok"):
                    deprecated_count += 1
                    logger.warning(f"Auto-deprecated tool '{tool_name}': {reason}")
                else:
                    logger.error(f"Failed to deprecate tool '{tool_name}': {deprecate_result.get('error')}")
        
        # 4. Log summary
        summary = dashboard.get("summary", {})
        logger.info(
            f"Tool evaluation complete: "
            f"{summary.get('healthy_count', 0)} healthy, "
            f"{summary.get('degraded_count', 0)} degraded, "
            f"{summary.get('failing_count', 0)} failing, "
            f"{deprecated_count} auto-deprecated"
        )
        
        return {
            "ok": True,
            "evaluated": len(ratings),
            "deprecated": deprecated_count,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Tool evaluation task failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def tool_optimization_task() -> Dict[str, Any]:
    """
    Periodic task to optimize tool selection based on ratings.
    
    Runs daily to:
    1. Update tool rankings based on recent performance
    2. Identify tools that should be prioritized
    3. Generate recommendations for tool improvements
    """
    try:
        state = get_shared_state()
        logger.info("Starting tool optimization task...")
        
        # Get current health dashboard
        dashboard = await tool_get_tool_health_dashboard(state)
        
        if not dashboard.get("ok"):
            return {"ok": False, "error": dashboard.get("error")}
        
        # Analyze patterns
        healthy_tools = dashboard.get("healthy", [])
        degraded_tools = dashboard.get("degraded", [])
        
        # Identify top performers
        top_tools = sorted(healthy_tools, key=lambda x: x.get("rating", 0), reverse=True)[:10]
        
        # Identify tools that need attention
        needs_attention = degraded_tools + dashboard.get("failing", [])
        
        logger.info(
            f"Tool optimization: {len(top_tools)} top performers, "
            f"{len(needs_attention)} tools need attention"
        )
        
        return {
            "ok": True,
            "top_tools": [t.get("tool") for t in top_tools],
            "needs_attention": [t.get("tool") for t in needs_attention],
            "summary": dashboard.get("summary", {})
        }
    except Exception as e:
        logger.error(f"Tool optimization task failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}

