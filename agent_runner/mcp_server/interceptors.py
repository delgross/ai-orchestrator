import logging
import json
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from agent_runner.agent_runner import get_shared_state, get_shared_engine

logger = logging.getLogger("agent_runner.mcp_server.interceptors")

class ToolInterceptor(ABC):
    """Abstract Base Class for Tool Interceptors."""
    
    @abstractmethod
    async def before_execution(self, tool_name: str, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called before tool execution.
        Args:
            tool_name: The name of the tool (e.g. "store_fact")
            args: The arguments passed by the client.
            context: Context metadata (e.g. {"client_name": "cursor"}).
        Returns:
            Modified args.
        Raises:
            Exception: To block execution.
        """
        pass

    @abstractmethod
    async def after_execution(self, tool_name: str, result: Any, context: Dict[str, Any]) -> Any:
        """
        Called after tool execution. Can modify result.
        """
        pass

class WriteOwnInterceptor(ToolInterceptor):
    """
    Enforces 'Write-Own' policy.
    If a tool attempts to write to a 'kb_id' that doesn't match the client name,
    it overrides it to match the client name.
    """
    async def before_execution(self, tool_name: str, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name in ["store_fact", "ingest_file", "delete_fact", "update_fact"]:
            client_name = context.get("client_name", "unknown")
            target_kb = args.get("kb_id")
            
            # If kb_id is missing or different, override it
            if not target_kb or target_kb != client_name:
                logger.info(f"[WriteOwnInterceptor] Client '{client_name}' tried to write to '{target_kb}'. Redirecting to '{client_name}'.")
                args["kb_id"] = client_name
        
        return args

    async def after_execution(self, tool_name: str, result: Any, context: Dict[str, Any]) -> Any:
        return result

class PrivacyInterceptor(ToolInterceptor):
    """
    Enforces 'Privacy' policy using memory_bank_config.
    """
    def __init__(self):
        self._cache = {} # (kb_id, client_name) -> (allowed: bool, timestamp: float)
        self._cache_ttl = 60.0

    async def before_execution(self, tool_name: str, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # [Refactor #5] Handle Resource Reads
        if tool_name == "read_resource":
            uri = args.get("uri")
            if uri and uri.startswith("memory://"):
                # Extract kb_id
                import re
                match = re.match(r"memory://([^/]+)/summary", uri)
                if match:
                    target_kb = match.group(1)
                    client_name = context.get("client_name", "unknown")
                    
                    # --- REUSED LOGIC (Ideally extract method) ---
                    from agent_runner.service_registry import ServiceRegistry
                    
                    # Check Cache
                    cache_key = (target_kb, client_name)
                    cached = self._cache.get(cache_key)
                    if cached:
                        allowed, ts = cached
                        if time.time() - ts < self._cache_ttl:
                            if not allowed:
                                 raise PermissionError(f"Access Denied (Cached): Memory Bank '{target_kb}' is PRIVATE.")
                            return args 

                    mem = ServiceRegistry.get_memory_server()
                    if not mem: 
                        raise PermissionError("Access Denied: System Memory Service Unavailable.")
                    
                    res = await mem.get_bank_config(target_kb)
                    is_allowed = True
                    owner = "unknown"
                    
                    if res.get("ok"):
                        config = res.get("config", {})
                        is_private = config.get("is_private", False)
                        owner = config.get("owner", "")
                        
                        if is_private and owner != client_name:
                             is_allowed = False
                    
                    self._cache[cache_key] = (is_allowed, time.time())
                    
                    if not is_allowed:
                         logger.warning(f"[PrivacyInterceptor] Access Denied. Client '{client_name}' tried to read private bank '{target_kb}' owned by '{owner}'.")
                         raise PermissionError(f"Access Denied: Memory Bank '{target_kb}' is PRIVATE and owned by '{owner}'.")

        if tool_name in ["query_facts", "semantic_search"]:
            target_kb = args.get("kb_id")
            client_name = context.get("client_name", "unknown")
            
            if target_kb:
                # Need to check config. 
                # Ideally we inject the memory_server instance or use the shared engine to get it?
                # For now using a direct call pattern via AgentEngine -> MemoryServer if possible
                # Or re-instantiate MemoryServer (lightweight if using HTTP)
                
                # Use ServiceRegistry to access MemoryServer without circular dependencies
                from agent_runner.service_registry import ServiceRegistry
                
                # Check Cache
                cache_key = (target_kb, client_name)
                cached = self._cache.get(cache_key)
                if cached:
                    allowed, ts = cached
                    if time.time() - ts < self._cache_ttl:
                        if not allowed:
                             raise PermissionError(f"Access Denied (Cached): Memory Bank '{target_kb}' is PRIVATE.")
                        return args # Allowed

                # Retrieve MemoryServer from registry
                mem = ServiceRegistry.get_memory_server()
                if not mem:
                    # Fail closed if memory server unavail
                    logger.warning("MemoryServer not registered in ServiceRegistry. Denying access.")
                    raise PermissionError("Access Denied: System Memory Service Unavailable.")
                
                res = await mem.get_bank_config(target_kb)
                
                # Default Allow if lookup fails (fail open or closed? Closed is safer)
                is_allowed = True
                
                if res.get("ok"):
                    config = res.get("config", {})
                    is_private = config.get("is_private", False)
                    owner = config.get("owner", "")
                    
                    if is_private and owner != client_name:
                         is_allowed = False
                
                # Update Cache
                self._cache[cache_key] = (is_allowed, time.time())
                
                if not is_allowed:
                     logger.warning(f"[PrivacyInterceptor] Access Denied. Client '{client_name}' tried to read private bank '{target_kb}' owned by '{owner}'.")
                     raise PermissionError(f"Access Denied: Memory Bank '{target_kb}' is PRIVATE and owned by '{owner}'.")
                
        return args

    async def after_execution(self, tool_name: str, result: Any, context: Dict[str, Any]) -> Any:
        # Filter list_memory_banks
        if tool_name == "list_memory_banks" and isinstance(result, dict) and "banks" in result:
             client_name = context.get("client_name", "unknown")
             # We need to filter out private banks that don't belong to us.
             # This requires checking config for EACH bank. Ideally list_memory_banks should support this internally.
             # But we can do it here.
             
             # Optimization: This might be slow if many banks.
             # For now, we trust the 'list' is public info, but the CONTENT is private.
             # Or we can iterate and check. 
             pass
             
        return result

class LoggingInterceptor(ToolInterceptor):
    """Log all MCP operations."""
    async def before_execution(self, tool_name: str, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        client = context.get("client_name", "unknown")
        logger.info(f"[MCP] Client='{client}' Tool='{tool_name}' Args={json.dumps(args)[:200]}...")
        return args

    async def after_execution(self, tool_name: str, result: Any, context: Dict[str, Any]) -> Any:
        return result
