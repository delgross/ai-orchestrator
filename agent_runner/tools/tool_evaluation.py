"""
Tool Evaluation and Rating System

Provides automatic tool evaluation, rating, and health monitoring.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from agent_runner.state import AgentState

logger = logging.getLogger("agent_runner.tools.tool_evaluation")


async def tool_evaluate_tool_health(state: AgentState, tool_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluate health of a specific tool or all tools.
    Calculates ratings based on performance metrics.
    """
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not initialized"}
        
        await state.memory.ensure_connected()
        
        if tool_name:
            # Evaluate single tool
            query = """
            SELECT tool, success_count, failure_count, reliability_score, last_used
            FROM tool_performance
            WHERE tool = $tool_name
            ORDER BY last_used DESC
            LIMIT 1;
            """
            from agent_runner.db_utils import run_query
            results = await run_query(state, query, {"tool_name": tool_name})
            
            if not results:
                return {"ok": False, "error": f"Tool '{tool_name}' not found in performance data"}
            
            perf = results[0]
            total = perf.get("success_count", 0) + perf.get("failure_count", 0)
            success_rate = perf.get("success_count", 0) / total if total > 0 else 0.0
            
            # Calculate overall rating (0.0-1.0)
            reliability = perf.get("reliability_score", 0.0)
            overall_rating = (success_rate * 0.6) + (reliability * 0.4)
            
            # Update or create rating
            rating_query = """
            UPSERT type::thing('tool_rating', $tool_name)
            SET tool_name = $tool_name,
                overall_rating = $overall_rating,
                success_rate = $success_rate,
                usage_count = $total,
                last_evaluated = time::now();
            """
            await run_query(state, rating_query, {
                "tool_name": tool_name,
                "overall_rating": overall_rating,
                "success_rate": success_rate,
                "total": total
            })
            
            return {
                "ok": True,
                "tool": tool_name,
                "rating": overall_rating,
                "success_rate": success_rate,
                "reliability": reliability,
                "usage_count": total
            }
        else:
            # Evaluate all tools
            query = """
            SELECT tool, success_count, failure_count, reliability_score, last_used
            FROM tool_performance;
            """
            from agent_runner.db_utils import run_query
            results = await run_query(state, query)
            
            ratings = []
            for perf in results or []:
                tool = perf.get("tool")
                total = perf.get("success_count", 0) + perf.get("failure_count", 0)
                if total == 0:
                    continue
                
                success_rate = perf.get("success_count", 0) / total
                reliability = perf.get("reliability_score", 0.0)
                overall_rating = (success_rate * 0.6) + (reliability * 0.4)
                
                # Update rating
                rating_query = """
                UPSERT type::thing('tool_rating', $tool_name)
                SET tool_name = $tool_name,
                    overall_rating = $overall_rating,
                    success_rate = $success_rate,
                    usage_count = $total,
                    last_evaluated = time::now();
                """
                await run_query(state, rating_query, {
                    "tool_name": tool,
                    "overall_rating": overall_rating,
                    "success_rate": success_rate,
                    "total": total
                })
                
                ratings.append({
                    "tool": tool,
                    "rating": overall_rating,
                    "success_rate": success_rate,
                    "reliability": reliability,
                    "usage_count": total
                })
            
            return {
                "ok": True,
                "ratings": sorted(ratings, key=lambda x: x["rating"], reverse=True),
                "count": len(ratings)
            }
    except Exception as e:
        logger.error(f"Tool evaluation failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def tool_get_tool_health_dashboard(state: AgentState) -> Dict[str, Any]:
    """
    Get comprehensive tool health dashboard.
    Categorizes tools by health status.
    """
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not initialized"}
        
        await state.memory.ensure_connected()
        
        # Get all ratings
        query = """
        SELECT tool_name, overall_rating, success_rate, usage_count, deprecated
        FROM tool_rating
        ORDER BY overall_rating DESC;
        """
        from agent_runner.db_utils import run_query
        results = await run_query(state, query)
        
        healthy = []
        degraded = []
        failing = []
        deprecated_list = []
        
        for rating in results or []:
            tool_name = rating.get("tool_name")
            overall_rating = rating.get("overall_rating", 0.0)
            is_deprecated = rating.get("deprecated", False)
            
            if is_deprecated:
                deprecated_list.append({
                    "tool": tool_name,
                    "rating": overall_rating,
                    "reason": rating.get("deprecation_reason", "Unknown")
                })
            elif overall_rating >= 0.7:
                healthy.append({
                    "tool": tool_name,
                    "rating": overall_rating,
                    "success_rate": rating.get("success_rate", 0.0),
                    "usage_count": rating.get("usage_count", 0)
                })
            elif overall_rating >= 0.4:
                degraded.append({
                    "tool": tool_name,
                    "rating": overall_rating,
                    "success_rate": rating.get("success_rate", 0.0),
                    "usage_count": rating.get("usage_count", 0)
                })
            else:
                failing.append({
                    "tool": tool_name,
                    "rating": overall_rating,
                    "success_rate": rating.get("success_rate", 0.0),
                    "usage_count": rating.get("usage_count", 0)
                })
        
        return {
            "ok": True,
            "healthy": healthy,
            "degraded": degraded,
            "failing": failing,
            "deprecated": deprecated_list,
            "summary": {
                "total": len(healthy) + len(degraded) + len(failing) + len(deprecated_list),
                "healthy_count": len(healthy),
                "degraded_count": len(degraded),
                "failing_count": len(failing),
                "deprecated_count": len(deprecated_list)
            }
        }
    except Exception as e:
        logger.error(f"Tool health dashboard failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def tool_deprecate_tool(state: AgentState, tool_name: str, reason: str) -> Dict[str, Any]:
    """
    Deprecate a tool (mark as deprecated).
    """
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not initialized"}
        
        await state.memory.ensure_connected()
        
        query = """
        UPDATE tool_rating
        SET deprecated = true,
            deprecation_reason = $reason
        WHERE tool_name = $tool_name;
        """
        from agent_runner.db_utils import run_query
        await run_query(state, query, {"tool_name": tool_name, "reason": reason})
        
        logger.warning(f"Tool '{tool_name}' deprecated: {reason}")
        
        return {
            "ok": True,
            "message": f"Tool '{tool_name}' deprecated",
            "reason": reason
        }
    except Exception as e:
        logger.error(f"Tool deprecation failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def tool_record_tool_usage(
    state: AgentState,
    tool_name: str,
    user_query: str,
    success: bool,
    latency_ms: float,
    context_length: int,
    model: str
) -> Dict[str, Any]:
    """
    Record detailed tool usage for analytics.
    """
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not initialized"}
        
        await state.memory.ensure_connected()
        
        query = """
        CREATE tool_usage_analytics SET
            tool_name = $tool_name,
            user_query = $user_query,
            success = $success,
            latency_ms = $latency_ms,
            context_length = $context_length,
            model = $model,
            timestamp = time::now();
        """
        from agent_runner.db_utils import run_query
        await run_query(state, query, {
            "tool_name": tool_name,
            "user_query": user_query[:500],  # Limit query length
            "success": success,
            "latency_ms": latency_ms,
            "context_length": context_length,
            "model": model
        })
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Tool usage recording failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}







