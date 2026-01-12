"""
Tool Management API Endpoints

Provides endpoints for tool registry, versioning, and management.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Body, HTTPException
from agent_runner.agent_runner import get_shared_state, get_shared_engine
from agent_runner.tool_categories import VALID_CATEGORIES, get_tool_category

router = APIRouter()
logger = logging.getLogger("agent_runner.routes.tools")


@router.get("/admin/tools/health")
async def get_tool_health():
    """Get comprehensive tool health dashboard."""
    from agent_runner.tools.tool_evaluation import tool_get_tool_health_dashboard
    state = get_shared_state()
    return await tool_get_tool_health_dashboard(state)


@router.post("/admin/tools/evaluate")
async def evaluate_tool_health(tool_name: Optional[str] = Body(None, embed=True)):
    """Evaluate health of a specific tool or all tools."""
    from agent_runner.tools.tool_evaluation import tool_evaluate_tool_health
    state = get_shared_state()
    return await tool_evaluate_tool_health(state, tool_name)


@router.post("/admin/tools/deprecate")
async def deprecate_tool(tool_name: str = Body(..., embed=True), reason: str = Body(..., embed=True)):
    """Deprecate a tool."""
    from agent_runner.tools.tool_evaluation import tool_deprecate_tool
    state = get_shared_state()
    return await tool_deprecate_tool(state, tool_name, reason)


@router.post("/admin/tools/register")
async def register_tool(tool_def: Dict[str, Any] = Body(...)):
    """
    Register a new tool dynamically.
    
    Body:
    {
        "name": "my_tool",
        "description": "Tool description",
        "parameters": {...},
        "implementation": "module.function",  # Optional: Python function path
        "category": "filesystem",  # Optional: auto-detected if not provided
        "version": "1.0.0",  # Optional
        "examples": ["example1", "example2"],  # Optional
        "prerequisites": {...}  # Optional
    }
    """
    state = get_shared_state()
    engine = get_shared_engine()
    
    try:
        tool_name = tool_def.get("name")
        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing 'name' field")
        
        # Validate tool definition
        if "description" not in tool_def:
            raise HTTPException(status_code=400, detail="Missing 'description' field")
        
        if "parameters" not in tool_def:
            raise HTTPException(status_code=400, detail="Missing 'parameters' field")
        
        # Auto-detect category if not provided
        category = tool_def.get("category")
        if not category:
            category = get_tool_category(tool_name, tool_def.get("description", ""))
            tool_def["category"] = category
        
        # Validate category
        if category and category not in VALID_CATEGORIES:
            logger.warning(f"Unknown category '{category}' for tool '{tool_name}', using 'other'")
            category = None
        
        # Create OpenAI-style tool definition
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_def["description"],
                "parameters": tool_def["parameters"]
            },
            "category": category,
            "version": tool_def.get("version", "1.0.0"),
            "examples": tool_def.get("examples", []),
            "prerequisites": tool_def.get("prerequisites", {}),
            "registered_at": time.time()
        }
        
        # Add to tool definitions (runtime only, not persisted to code)
        # For persistence, we'd need to store in database and reload on startup
        engine.executor.tool_definitions.append(openai_tool)
        
        # Index in database for semantic search
        if hasattr(state, "memory") and state.memory:
            await state.memory.index_tools([openai_tool])
        
        # Store version if provided
        if "version" in tool_def:
            from agent_runner.db_utils import run_query
            version_query = """
            CREATE tool_version SET
                tool_name = $tool_name,
                version = $version,
                changelog = $changelog,
                created_at = time::now();
            """
            await run_query(state, version_query, {
                "tool_name": tool_name,
                "version": tool_def.get("version", "1.0.0"),
                "changelog": tool_def.get("changelog")
            })
        
        logger.info(f"Registered new tool: {tool_name} (category: {category})")
        
        return {
            "ok": True,
            "tool_id": tool_name,
            "category": category,
            "message": f"Tool '{tool_name}' registered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool registration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/tools/versions/{tool_name}")
async def get_tool_versions(tool_name: str):
    """Get version history for a tool."""
    state = get_shared_state()
    
    try:
        from agent_runner.db_utils import run_query
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not initialized"}
        
        query = """
        SELECT * FROM tool_version
        WHERE tool_name = $tool_name
        ORDER BY created_at DESC;
        """
        results = await run_query(state, query, {"tool_name": tool_name})
        
        return {
            "ok": True,
            "tool": tool_name,
            "versions": results or []
        }
    except Exception as e:
        logger.error(f"Failed to get tool versions: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


@router.get("/admin/tools/analytics")
async def get_tool_analytics(tool_name: Optional[str] = None, limit: int = 100):
    """Get tool usage analytics."""
    state = get_shared_state()
    
    try:
        from agent_runner.db_utils import run_query
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "error": "Memory server not initialized"}
        
        if tool_name:
            query = """
            SELECT * FROM tool_usage_analytics
            WHERE tool_name = $tool_name
            ORDER BY timestamp DESC
            LIMIT $limit;
            """
            results = await run_query(state, query, {"tool_name": tool_name, "limit": limit})
        else:
            # Aggregate analytics
            query = """
            SELECT tool_name,
                   count() as usage_count,
                   math::avg(latency_ms) as avg_latency,
                   math::sum(IF success THEN 1 ELSE 0 END) as success_count,
                   math::sum(IF success THEN 0 ELSE 1 END) as failure_count
            FROM tool_usage_analytics
            GROUP BY tool_name
            ORDER BY usage_count DESC
            LIMIT $limit;
            """
            results = await run_query(state, query, {"limit": limit})
        
        return {
            "ok": True,
            "analytics": results or [],
            "count": len(results) if results else 0
        }
    except Exception as e:
        logger.error(f"Failed to get tool analytics: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


@router.get("/admin/tools/categories")
async def get_tool_categories():
    """Get all available tool categories."""
    from agent_runner.tool_categories import CATEGORY_HIERARCHY, CATEGORY_SYNONYMS
    
    return {
        "ok": True,
        "categories": list(VALID_CATEGORIES),
        "hierarchy": CATEGORY_HIERARCHY,
        "synonyms": CATEGORY_SYNONYMS
    }

