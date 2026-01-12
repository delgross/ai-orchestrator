"""
Tool Marketplace

Centralized tool discovery, installation, and management system.
"""

import logging
import json
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from pathlib import Path
from agent_runner.state import AgentState
from agent_runner.db_utils import run_query
from agent_runner.tools.tool_evaluation import tool_evaluate_tool_health

logger = logging.getLogger("agent_runner.marketplace")


class ToolMarketplace:
    """
    Tool marketplace for discovering, installing, and managing tools.
    
    Supports:
    - NPM-based MCP servers (primary)
    - Python package tools
    - Custom tool definitions
    - Community submissions
    """
    
    def __init__(self, state: AgentState):
        self.state = state
        self.npm_registry_url = "https://registry.npmjs.org"
        self.marketplace_cache: Dict[str, Any] = {}
    
    async def search_tools(
        self,
        query: str,
        category: Optional[str] = None,
        min_rating: Optional[float] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search for tools in the marketplace.
        
        Searches:
        1. NPM registry (MCP servers)
        2. Local tool registry
        3. Community submissions
        """
        try:
            results = []
            
            # 1. Search NPM registry for MCP servers
            npm_results = await self._search_npm_mcp_servers(query, limit=limit)
            results.extend(npm_results)
            
            # 2. Search local tool registry
            local_results = await self._search_local_tools(query, category, min_rating)
            results.extend(local_results)
            
            # 3. Search community submissions (if implemented)
            # community_results = await self._search_community_tools(query)
            # results.extend(community_results)
            
            # Deduplicate and sort by relevance
            unique_results = self._deduplicate_tools(results)
            sorted_results = sorted(
                unique_results,
                key=lambda x: x.get("relevance_score", 0),
                reverse=True
            )[:limit]
            
            return {
                "ok": True,
                "query": query,
                "results": sorted_results,
                "count": len(sorted_results)
            }
        except Exception as e:
            logger.error(f"Tool search failed: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    async def _search_npm_mcp_servers(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search NPM registry for MCP server packages."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Search NPM registry
                search_url = f"{self.npm_registry_url}/-/v1/search"
                params = {
                    "text": f"mcp server {query}",
                    "size": limit
                }
                response = await client.get(search_url, params=params)
                
                if response.status_code != 200:
                    logger.warning(f"NPM search failed: {response.status_code}")
                    return []
                
                data = response.json()
                results = []
                
                for package in data.get("objects", [])[:limit]:
                    pkg_info = package.get("package", {})
                    name = pkg_info.get("name", "")
                    
                    # Filter for MCP servers
                    if "mcp" in name.lower() or "modelcontextprotocol" in name.lower():
                        results.append({
                            "name": name,
                            "description": pkg_info.get("description", ""),
                            "version": pkg_info.get("version", ""),
                            "type": "npm_mcp",
                            "source": "npm",
                            "install_command": f"npx -y {name}",
                            "relevance_score": package.get("score", {}).get("final", 0.0),
                            "downloads": package.get("score", {}).get("detail", {}).get("popularity", 0.0)
                        })
                
                return results
        except Exception as e:
            logger.debug(f"NPM search error: {e}")
            return []
    
    async def _search_local_tools(
        self,
        query: str,
        category: Optional[str] = None,
        min_rating: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search locally registered tools."""
        try:
            if not hasattr(self.state, "memory") or not self.state.memory:
                return []
            
            await self.state.memory.ensure_connected()
            
            # Search tool definitions
            search_query = """
            SELECT name, description
            FROM tool_definition
            WHERE description CONTAINS $query OR name CONTAINS $query
            LIMIT 20;
            """
            results = await run_query(self.state, search_query, {"query": query})
            
            tools = []
            for tool in results or []:
                tool_name = tool.get("name", "")
                
                # Get rating if available
                rating_query = """
                SELECT overall_rating, deprecated
                FROM tool_rating
                WHERE tool_name = $tool_name;
                """
                rating_result = await run_query(self.state, rating_query, {"tool_name": tool_name})
                
                rating = None
                deprecated = False
                if rating_result:
                    rating = rating_result[0].get("overall_rating")
                    deprecated = rating_result[0].get("deprecated", False)
                
                # Filter by rating if specified
                if min_rating and (rating is None or rating < min_rating):
                    continue
                
                # Filter by category if specified
                if category:
                    from agent_runner.tool_categories import get_tool_category
                    tool_category = get_tool_category(tool_name, tool.get("description", ""))
                    if tool_category != category:
                        continue
                
                tools.append({
                    "name": tool_name,
                    "description": tool.get("description", ""),
                    "type": "builtin",
                    "source": "local",
                    "rating": rating,
                    "deprecated": deprecated,
                    "relevance_score": 1.0 if rating else 0.5
                })
            
            return tools
        except Exception as e:
            logger.debug(f"Local tool search error: {e}")
            return []
    
    def _deduplicate_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate tools based on name."""
        seen = set()
        unique = []
        for tool in tools:
            name = tool.get("name", "")
            if name and name not in seen:
                seen.add(name)
                unique.append(tool)
        return unique
    
    async def get_tool_info(self, tool_id: str, source: str = "auto") -> Dict[str, Any]:
        """
        Get detailed information about a tool.
        
        Args:
            tool_id: Tool identifier (package name, tool name, etc.)
            source: Source type ("npm", "local", "auto")
        """
        try:
            # Auto-detect source
            if source == "auto":
                if tool_id.startswith("@") or "/" in tool_id:
                    source = "npm"
                elif tool_id.startswith("mcp__"):
                    source = "local"
                else:
                    # Try local first, then npm
                    local_info = await self._get_local_tool_info(tool_id)
                    if local_info.get("ok"):
                        return local_info
                    source = "npm"
            
            if source == "npm":
                return await self._get_npm_tool_info(tool_id)
            elif source == "local":
                return await self._get_local_tool_info(tool_id)
            else:
                return {"ok": False, "error": f"Unknown source: {source}"}
        except Exception as e:
            logger.error(f"Failed to get tool info: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    async def _get_npm_tool_info(self, package_name: str) -> Dict[str, Any]:
        """Get information about an NPM package."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.npm_registry_url}/{package_name}"
                response = await client.get(url)
                
                if response.status_code != 200:
                    return {"ok": False, "error": f"Package not found: {package_name}"}
                
                data = response.json()
                latest_version = data.get("dist-tags", {}).get("latest", "")
                latest_data = data.get("versions", {}).get(latest_version, {})
                
                return {
                    "ok": True,
                    "name": package_name,
                    "description": latest_data.get("description", ""),
                    "version": latest_version,
                    "type": "npm_mcp",
                    "source": "npm",
                    "homepage": latest_data.get("homepage"),
                    "repository": latest_data.get("repository", {}).get("url", ""),
                    "keywords": latest_data.get("keywords", []),
                    "author": latest_data.get("author", {}),
                    "license": latest_data.get("license", ""),
                    "dependencies": latest_data.get("dependencies", {}),
                    "install_command": f"npx -y {package_name}",
                    "downloads": data.get("downloads", {}).get("lastMonth", 0)
                }
        except Exception as e:
            logger.error(f"Failed to get NPM tool info: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    async def _get_local_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a locally registered tool."""
        try:
            if not hasattr(self.state, "memory") or not self.state.memory:
                return {"ok": False, "error": "Memory server not available"}
            
            await self.state.memory.ensure_connected()
            
            # Get tool definition
            tool_query = """
            SELECT name, description
            FROM tool_definition
            WHERE name = $tool_name;
            """
            tool_result = await run_query(self.state, tool_query, {"tool_name": tool_name})
            
            if not tool_result:
                return {"ok": False, "error": f"Tool not found: {tool_name}"}
            
            tool_def = tool_result[0]
            
            # Get rating
            rating_query = """
            SELECT overall_rating, success_rate, usage_count, deprecated, deprecation_reason
            FROM tool_rating
            WHERE tool_name = $tool_name;
            """
            rating_result = await run_query(self.state, rating_query, {"tool_name": tool_name})
            
            # Get version history
            version_query = """
            SELECT version, changelog, created_at
            FROM tool_version
            WHERE tool_name = $tool_name
            ORDER BY created_at DESC;
            """
            version_result = await run_query(self.state, version_query, {"tool_name": tool_name})
            
            # Get usage analytics
            analytics_query = """
            SELECT 
                count() as usage_count,
                math::avg(latency_ms) as avg_latency,
                math::sum(IF success THEN 1 ELSE 0 END) as success_count,
                math::sum(IF success THEN 0 ELSE 1 END) as failure_count
            FROM tool_usage_analytics
            WHERE tool_name = $tool_name;
            """
            analytics_result = await run_query(self.state, analytics_query, {"tool_name": tool_name})
            
            return {
                "ok": True,
                "name": tool_name,
                "description": tool_def.get("description", ""),
                "type": "builtin",
                "source": "local",
                "rating": rating_result[0].get("overall_rating") if rating_result else None,
                "success_rate": rating_result[0].get("success_rate") if rating_result else None,
                "usage_count": rating_result[0].get("usage_count", 0) if rating_result else 0,
                "deprecated": rating_result[0].get("deprecated", False) if rating_result else False,
                "deprecation_reason": rating_result[0].get("deprecation_reason") if rating_result else None,
                "versions": version_result or [],
                "analytics": analytics_result[0] if analytics_result else {}
            }
        except Exception as e:
            logger.error(f"Failed to get local tool info: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    async def install_tool(
        self,
        tool_id: str,
        source: str = "auto",
        name: Optional[str] = None,
        args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Install a tool from the marketplace.
        
        Handles:
        - NPM package installation
        - MCP server configuration
        - Dependency resolution
        - Tool registration
        """
        try:
            # Get tool info first
            tool_info = await self.get_tool_info(tool_id, source)
            if not tool_info.get("ok"):
                return tool_info
            
            # Determine installation method
            if tool_info.get("type") == "npm_mcp":
                return await self._install_npm_mcp_tool(tool_id, name, args)
            elif tool_info.get("type") == "builtin":
                return {"ok": False, "error": "Built-in tools cannot be installed (already available)"}
            else:
                return {"ok": False, "error": f"Unknown tool type: {tool_info.get('type')}"}
        except Exception as e:
            logger.error(f"Tool installation failed: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    async def _install_npm_mcp_tool(
        self,
        package_name: str,
        name: Optional[str] = None,
        args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Install an NPM-based MCP server."""
        try:
            # Derive server name
            if not name:
                parts = package_name.split("/")[-1].replace("server-", "").replace("-mcp", "")
                name = parts
            
            # Validate package exists
            import asyncio
            val_proc = await asyncio.create_subprocess_exec(
                "npm", "view", package_name, "name",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await val_proc.communicate()
            if val_proc.returncode != 0:
                return {"ok": False, "error": f"NPM Package '{package_name}' not found"}
            
            # Construct MCP server config
            cmd_list = ["npx", "-y", package_name]
            if args:
                cmd_list.extend(args)
            
            config = {
                "cmd": cmd_list,
                "requires_internet": True,
                "type": "stdio"
            }
            
            # Install via state
            await self.state.add_mcp_server(name, config)
            
            # Trigger tool discovery
            from agent_runner.service_registry import ServiceRegistry
            try:
                engine = ServiceRegistry.get_engine()
                await engine.discover_mcp_tools()
            except RuntimeError:
                logger.warning("Could not access engine for tool discovery")
            
            # Register tool version
            if hasattr(self.state, "memory") and self.state.memory:
                version_query = """
                CREATE tool_version SET
                    tool_name = $tool_name,
                    version = $version,
                    changelog = $changelog,
                    created_at = time::now();
                """
                await run_query(self.state, version_query, {
                    "tool_name": f"mcp__{name}",
                    "version": "1.0.0",  # Could fetch from npm
                    "changelog": f"Installed from marketplace: {package_name}"
                })
            
            logger.info(f"Installed tool '{name}' from package '{package_name}'")
            
            return {
                "ok": True,
                "message": f"Successfully installed '{package_name}' as '{name}'",
                "server": name,
                "package": package_name
            }
        except Exception as e:
            logger.error(f"NPM tool installation failed: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    async def update_tool(self, tool_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a tool to the latest version.
        
        For NPM tools: Updates the package
        For local tools: Updates from registry if available
        """
        try:
            # Get current tool info
            tool_info = await self.get_tool_info(tool_name, source="auto")
            if not tool_info.get("ok"):
                return tool_info
            
            if tool_info.get("type") == "npm_mcp":
                # For NPM, reinstall with latest version
                package_name = tool_info.get("name")
                return await self._install_npm_mcp_tool(package_name, name=tool_name.split("__")[-1] if "__" in tool_name else None)
            else:
                return {"ok": False, "error": "Tool updates not supported for this type"}
        except Exception as e:
            logger.error(f"Tool update failed: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    async def submit_tool(self, tool_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a tool to the community marketplace.
        
        This would typically:
        1. Validate tool definition
        2. Store in community registry
        3. Queue for review (if moderation enabled)
        4. Make available to other users
        """
        try:
            # Validate tool definition
            required_fields = ["name", "description", "parameters"]
            for field in required_fields:
                if field not in tool_definition:
                    return {"ok": False, "error": f"Missing required field: {field}"}
            
            # For now, just register locally
            # In a full implementation, this would submit to a community registry
            from agent_runner.routes.tools import register_tool
            result = await register_tool(tool_definition)
            
            if result.get("ok"):
                logger.info(f"Tool '{tool_definition.get('name')}' submitted to marketplace")
            
            return result
        except Exception as e:
            logger.error(f"Tool submission failed: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    async def browse_tools(
        self,
        category: Optional[str] = None,
        sort_by: str = "popularity",
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Browse tools in the marketplace.
        
        Args:
            category: Filter by category
            sort_by: Sort by "popularity", "rating", "newest", "downloads"
            limit: Maximum results
        """
        try:
            # Get popular NPM MCP servers
            npm_tools = await self._get_popular_npm_tools(limit=limit)
            
            # Get local tools
            local_tools = await self._search_local_tools("", category, None)
            
            # Combine and sort
            all_tools = npm_tools + local_tools
            
            # Apply sorting
            if sort_by == "rating":
                all_tools.sort(key=lambda x: x.get("rating", 0) or 0, reverse=True)
            elif sort_by == "downloads":
                all_tools.sort(key=lambda x: x.get("downloads", 0), reverse=True)
            elif sort_by == "newest":
                all_tools.sort(key=lambda x: x.get("created_at", 0), reverse=True)
            else:  # popularity (default)
                all_tools.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            return {
                "ok": True,
                "tools": all_tools[:limit],
                "count": len(all_tools[:limit]),
                "category": category,
                "sort_by": sort_by
            }
        except Exception as e:
            logger.error(f"Browse tools failed: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    async def _get_popular_npm_tools(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get popular NPM MCP server packages."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Search for popular MCP packages
                search_url = f"{self.npm_registry_url}/-/v1/search"
                params = {
                    "text": "modelcontextprotocol",
                    "size": limit,
                    "quality": 0.65,
                    "popularity": 0.98,
                    "maintenance": 0.5
                }
                response = await client.get(search_url, params=params)
                
                if response.status_code != 200:
                    return []
                
                data = response.json()
                tools = []
                
                for package in data.get("objects", [])[:limit]:
                    pkg_info = package.get("package", {})
                    name = pkg_info.get("name", "")
                    
                    if "mcp" in name.lower() or "modelcontextprotocol" in name.lower():
                        tools.append({
                            "name": name,
                            "description": pkg_info.get("description", ""),
                            "version": pkg_info.get("version", ""),
                            "type": "npm_mcp",
                            "source": "npm",
                            "downloads": package.get("score", {}).get("detail", {}).get("popularity", 0.0),
                            "relevance_score": package.get("score", {}).get("final", 0.0)
                        })
                
                return tools
        except Exception as e:
            logger.debug(f"Failed to get popular NPM tools: {e}")
            return []







