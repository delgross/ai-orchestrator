"""
Tool Marketplace API Endpoints

Provides endpoints for tool discovery, installation, and management.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Body, HTTPException, Query
from agent_runner.agent_runner import get_shared_state
from agent_runner.marketplace import ToolMarketplace

router = APIRouter()
logger = logging.getLogger("agent_runner.routes.marketplace")


@router.get("/marketplace/search")
async def search_tools(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_rating: Optional[float] = Query(None, description="Minimum rating (0.0-1.0)"),
    limit: int = Query(20, description="Maximum results")
) -> Dict[str, Any]:
    """Search for tools in the marketplace."""
    state = get_shared_state()
    marketplace = ToolMarketplace(state)
    return await marketplace.search_tools(q, category, min_rating, limit)


@router.get("/marketplace/browse")
async def browse_tools(
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: str = Query("popularity", description="Sort by: popularity, rating, newest, downloads"),
    limit: int = Query(50, description="Maximum results")
) -> Dict[str, Any]:
    """Browse tools in the marketplace."""
    state = get_shared_state()
    marketplace = ToolMarketplace(state)
    return await marketplace.browse_tools(category, sort_by, limit)


@router.get("/marketplace/tools/{tool_id}")
async def get_tool_info(
    tool_id: str,
    source: str = Query("auto", description="Source: auto, npm, local")
) -> Dict[str, Any]:
    """Get detailed information about a tool."""
    state = get_shared_state()
    marketplace = ToolMarketplace(state)
    return await marketplace.get_tool_info(tool_id, source)


@router.post("/marketplace/install")
async def install_tool(
    tool_id: str = Body(..., embed=True, description="Tool identifier (package name, tool name)"),
    source: str = Body("auto", embed=True, description="Source: auto, npm, local"),
    name: Optional[str] = Body(None, embed=True, description="Custom name for the tool"),
    args: Optional[List[str]] = Body(None, embed=True, description="Additional arguments for installation")
) -> Dict[str, Any]:
    """Install a tool from the marketplace."""
    state = get_shared_state()
    marketplace = ToolMarketplace(state)
    return await marketplace.install_tool(tool_id, source, name, args)


@router.post("/marketplace/update")
async def update_tool(
    tool_name: str = Body(..., embed=True, description="Tool name to update"),
    version: Optional[str] = Body(None, embed=True, description="Specific version (default: latest)")
) -> Dict[str, Any]:
    """Update a tool to the latest version."""
    state = get_shared_state()
    marketplace = ToolMarketplace(state)
    return await marketplace.update_tool(tool_name, version)


@router.post("/marketplace/submit")
async def submit_tool(
    tool_definition: Dict[str, Any] = Body(..., description="Tool definition to submit")
) -> Dict[str, Any]:
    """Submit a tool to the community marketplace."""
    state = get_shared_state()
    marketplace = ToolMarketplace(state)
    return await marketplace.submit_tool(tool_definition)


@router.get("/marketplace/categories")
async def get_marketplace_categories() -> Dict[str, Any]:
    """Get available tool categories in the marketplace."""
    from agent_runner.tool_categories import VALID_CATEGORIES, CATEGORY_HIERARCHY
    return {
        "ok": True,
        "categories": list(VALID_CATEGORIES),
        "hierarchy": CATEGORY_HIERARCHY
    }








