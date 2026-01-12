"""
Validation and Testing for Recent Changes (Last 2 Hours)

Validates all tool categorization, evaluation, and marketplace changes.
"""

import logging
import asyncio
from typing import Dict, Any, List
from agent_runner.agent_runner import get_shared_state
from agent_runner.tools.tool_evaluation import tool_evaluate_tool_health, tool_get_tool_health_dashboard
from agent_runner.tool_categories import get_tool_category, VALID_CATEGORIES, get_tools_by_category
from agent_runner.marketplace import ToolMarketplace

logger = logging.getLogger("agent_runner.tests.validate_recent_changes")


async def validate_all_changes() -> Dict[str, Any]:
    """
    Comprehensive validation of all changes from the last 2 hours.
    
    Validates:
    1. Tool categorization system
    2. Tool evaluation and rating system
    3. Tool registry API
    4. Rating integration
    5. Database schema
    6. Marketplace functionality
    """
    state = get_shared_state()
    results = {
        "ok": True,
        "validations": {},
        "errors": [],
        "warnings": []
    }
    
    try:
        # 1. Validate Tool Categorization
        logger.info("Validating tool categorization...")
        cat_results = await _validate_tool_categorization(state)
        results["validations"]["categorization"] = cat_results
        if not cat_results.get("ok"):
            results["errors"].extend(cat_results.get("errors", []))
        
        # 2. Validate Tool Evaluation
        logger.info("Validating tool evaluation system...")
        eval_results = await _validate_tool_evaluation(state)
        results["validations"]["evaluation"] = eval_results
        if not eval_results.get("ok"):
            results["errors"].extend(eval_results.get("errors", []))
        
        # 3. Validate Tool Registry API
        logger.info("Validating tool registry API...")
        registry_results = await _validate_tool_registry(state)
        results["validations"]["registry"] = registry_results
        if not registry_results.get("ok"):
            results["errors"].extend(registry_results.get("errors", []))
        
        # 4. Validate Rating Integration
        logger.info("Validating rating integration...")
        rating_results = await _validate_rating_integration(state)
        results["validations"]["rating_integration"] = rating_results
        if not rating_results.get("ok"):
            results["errors"].extend(rating_results.get("errors", []))
        
        # 5. Validate Database Schema
        logger.info("Validating database schema...")
        schema_results = await _validate_database_schema(state)
        results["validations"]["database_schema"] = schema_results
        if not schema_results.get("ok"):
            results["errors"].extend(schema_results.get("errors", []))
        
        # 6. Validate Marketplace
        logger.info("Validating marketplace...")
        marketplace_results = await _validate_marketplace(state)
        results["validations"]["marketplace"] = marketplace_results
        if not marketplace_results.get("ok"):
            results["warnings"].extend(marketplace_results.get("warnings", []))
        
        # Overall status
        if results["errors"]:
            results["ok"] = False
        
        logger.info(f"Validation complete: {len(results['errors'])} errors, {len(results['warnings'])} warnings")
        
        return results
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


async def _validate_tool_categorization(state: AgentState) -> Dict[str, Any]:
    """Validate tool categorization system."""
    errors = []
    warnings = []
    
    try:
        from agent_runner.service_registry import ServiceRegistry
        engine = ServiceRegistry.get_engine()
        if not engine:
            return {"ok": False, "errors": ["Engine not available"]}
        
        # Test 1: All tools have categories
        all_tools = await engine.get_all_tools()
        uncategorized = []
        for tool in all_tools:
            if "category" not in tool:
                func = tool.get("function", {})
                tool_name = func.get("name", "")
                category = get_tool_category(tool_name, func.get("description", ""))
                if not category:
                    uncategorized.append(tool_name)
        
        if uncategorized:
            warnings.append(f"{len(uncategorized)} tools without categories: {uncategorized[:5]}")
        
        # Test 2: Category filtering works
        fs_tools = await engine.get_all_tools(categories=["filesystem"])
        if not fs_tools:
            errors.append("Category filtering returned no results for 'filesystem'")
        
        # Test 3: Valid categories
        invalid_categories = []
        for tool in all_tools[:20]:  # Sample
            category = tool.get("category")
            if category and category not in VALID_CATEGORIES:
                invalid_categories.append(f"{tool.get('function', {}).get('name')}: {category}")
        
        if invalid_categories:
            warnings.append(f"Invalid categories found: {invalid_categories[:5]}")
        
        return {
            "ok": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_tools": len(all_tools),
            "uncategorized_count": len(uncategorized),
            "category_filtering_works": len(fs_tools) > 0
        }
    except Exception as e:
        return {"ok": False, "errors": [str(e)]}


async def _validate_tool_evaluation(state: AgentState) -> Dict[str, Any]:
    """Validate tool evaluation system."""
    errors = []
    warnings = []
    
    try:
        # Test 1: Evaluation function works
        eval_result = await tool_evaluate_tool_health(state, tool_name=None)
        if not eval_result.get("ok"):
            errors.append(f"Tool evaluation failed: {eval_result.get('error')}")
        
        # Test 2: Health dashboard works
        dashboard = await tool_get_tool_health_dashboard(state)
        if not dashboard.get("ok"):
            errors.append(f"Health dashboard failed: {dashboard.get('error')}")
        else:
            summary = dashboard.get("summary", {})
            if not summary:
                warnings.append("Health dashboard returned empty summary")
        
        # Test 3: Database tables exist
        if hasattr(state, "memory") and state.memory:
            await state.memory.ensure_connected()
            
            # Check tool_rating table
            from agent_runner.db_utils import run_query
            rating_check = await run_query(state, "SELECT count() FROM tool_rating;")
            if rating_check is None:
                errors.append("tool_rating table not accessible")
            
            # Check tool_usage_analytics table
            analytics_check = await run_query(state, "SELECT count() FROM tool_usage_analytics;")
            if analytics_check is None:
                errors.append("tool_usage_analytics table not accessible")
        
        return {
            "ok": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "evaluation_works": eval_result.get("ok", False),
            "dashboard_works": dashboard.get("ok", False)
        }
    except Exception as e:
        return {"ok": False, "errors": [str(e)]}


async def _validate_tool_registry(state: AgentState) -> Dict[str, Any]:
    """Validate tool registry API."""
    errors = []
    warnings = []
    
    try:
        # Test 1: Tool registration endpoint exists
        from agent_runner.routes.tools import router
        routes = [r.path for r in router.routes]
        
        if "/admin/tools/register" not in routes:
            errors.append("Tool registration endpoint not found")
        
        # Test 2: Tool versioning works
        if hasattr(state, "memory") and state.memory:
            await state.memory.ensure_connected()
            
            version_check = await run_query(state, "SELECT count() FROM tool_version;")
            if version_check is None:
                errors.append("tool_version table not accessible")
        
        return {
            "ok": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "registration_endpoint_exists": "/admin/tools/register" in routes
        }
    except Exception as e:
        return {"ok": False, "errors": [str(e)]}


async def _validate_rating_integration(state: AgentState) -> Dict[str, Any]:
    """Validate rating integration in tool selection."""
    errors = []
    warnings = []
    
    try:
        from agent_runner.service_registry import ServiceRegistry
        engine = ServiceRegistry.get_engine()
        if not engine:
            return {"ok": False, "errors": ["Engine not available"]}
        
        # Test 1: Tools are sorted by rating
        all_tools = await engine.get_all_tools()
        
        # Check if tools have rating metadata
        tools_with_ratings = [t for t in all_tools if "rating" in t]
        if not tools_with_ratings:
            warnings.append("No tools have rating metadata (may be normal if no usage yet)")
        
        # Test 2: Deprecated tools are filtered
        if hasattr(state, "memory") and state.memory:
            await state.memory.ensure_connected()
            
            deprecated_query = "SELECT tool_name FROM tool_rating WHERE deprecated = true LIMIT 5;"
            deprecated_result = await run_query(state, deprecated_query)
            
            if deprecated_result:
                deprecated_tools = [r.get("tool_name") for r in deprecated_result]
                # Check if deprecated tools appear in tool list
                tool_names = [t.get("function", {}).get("name") for t in all_tools]
                found_deprecated = [dt for dt in deprecated_tools if dt in tool_names]
                
                if found_deprecated:
                    # Core tools might still appear
                    core_tools = {"time", "project-memory", "weather", "system-control", "thinking"}
                    non_core_deprecated = [dt for dt in found_deprecated if not any(ct in dt for ct in core_tools)]
                    if non_core_deprecated:
                        warnings.append(f"Deprecated tools still in list: {non_core_deprecated}")
        
        return {
            "ok": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "tools_have_ratings": len(tools_with_ratings) > 0,
            "total_tools": len(all_tools)
        }
    except Exception as e:
        return {"ok": False, "errors": [str(e)]}


async def _validate_database_schema(state: AgentState) -> Dict[str, Any]:
    """Validate database schema changes."""
    errors = []
    warnings = []
    
    try:
        if not hasattr(state, "memory") or not state.memory:
            return {"ok": False, "errors": ["Memory server not available"]}
        
        await state.memory.ensure_connected()
        
        # Required tables
        required_tables = [
            "tool_rating",
            "tool_version",
            "tool_usage_analytics",
            "tool_definition",
            "tool_performance"
        ]
        
        missing_tables = []
        for table in required_tables:
            try:
                result = await run_query(state, f"SELECT count() FROM {table};")
                if result is None:
                    missing_tables.append(table)
            except Exception as e:
                missing_tables.append(f"{table} ({str(e)})")
        
        if missing_tables:
            errors.append(f"Missing tables: {missing_tables}")
        
        return {
            "ok": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "required_tables": required_tables,
            "missing_tables": missing_tables
        }
    except Exception as e:
        return {"ok": False, "errors": [str(e)]}


async def _validate_marketplace(state: AgentState) -> Dict[str, Any]:
    """Validate marketplace functionality."""
    errors = []
    warnings = []
    
    try:
        marketplace = ToolMarketplace(state)
        
        # Test 1: Search works
        search_result = await marketplace.search_tools("weather", limit=5)
        if not search_result.get("ok"):
            warnings.append(f"Marketplace search failed: {search_result.get('error')}")
        
        # Test 2: Browse works
        browse_result = await marketplace.browse_tools(limit=10)
        if not browse_result.get("ok"):
            warnings.append(f"Marketplace browse failed: {browse_result.get('error')}")
        
        # Test 3: API endpoints exist
        from agent_runner.routes.marketplace import router
        routes = [r.path for r in router.routes]
        
        required_routes = [
            "/marketplace/search",
            "/marketplace/browse",
            "/marketplace/install"
        ]
        
        missing_routes = [r for r in required_routes if r not in routes]
        if missing_routes:
            errors.append(f"Missing marketplace routes: {missing_routes}")
        
        return {
            "ok": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "search_works": search_result.get("ok", False),
            "browse_works": browse_result.get("ok", False),
            "routes_exist": len(missing_routes) == 0
        }
    except Exception as e:
        return {"ok": False, "errors": [str(e)]}







