"""
Memory Client Abstraction Layer

Provides a unified interface for memory operations that can be implemented
by different backends (direct memory server, MCP proxy, external services).

This abstraction allows swapping memory implementations without changing
engine code, while providing performance optimizations for direct access.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Fact:
    """Represents a memory fact."""
    entity: str
    relation: str
    target: str
    confidence: float = 1.0
    kb_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SearchResult:
    """Result of a semantic search operation."""
    content: List[Dict[str, Any]]
    total_found: int = 0
    search_time: float = 0.0

class MemoryClient(ABC):
    """
    Abstract base class for memory operations.

    Implementations can be:
    - DirectMemoryClient: Direct calls to in-process memory server (fastest)
    - McpMemoryClient: MCP proxy calls to memory server (isolated)
    - External clients: Redis, PostgreSQL, etc.
    """

    @abstractmethod
    async def semantic_search(self, query: str, limit: int = 10, **kwargs) -> SearchResult:
        """Perform semantic search for relevant facts."""
        pass

    @abstractmethod
    async def query_facts(self, kb_id: Optional[str] = None, entity: Optional[str] = None,
                         relation: Optional[str] = None, limit: int = 50, **kwargs) -> List[Fact]:
        """Query facts with optional filtering."""
        pass

    @abstractmethod
    async def store_fact(self, entity: str, relation: str, target: str,
                        confidence: float = 1.0, kb_id: Optional[str] = None, **kwargs) -> bool:
        """Store a new fact in memory."""
        pass

    @abstractmethod
    async def store_episode(self, request_id: str, messages: List[Dict[str, Any]], **kwargs) -> bool:
        """Store a conversation episode."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if the memory backend is healthy and accessible."""
        pass


class DirectMemoryClient(MemoryClient):
    """
    Direct memory client that calls the in-process memory server.

    This provides the best performance with zero subprocess overhead,
    but loses process isolation.
    """

    def __init__(self, memory_server):
        self.memory = memory_server

    async def semantic_search(self, query: str, limit: int = 10, **kwargs) -> SearchResult:
        """Direct call to memory server semantic search."""
        try:
            result = await self.memory.semantic_search(query, limit=limit)
            return SearchResult(
                content=result.get("content", []),
                total_found=result.get("total_found", 0),
                search_time=result.get("search_time", 0.0)
            )
        except Exception as e:
            logger.error(f"Direct semantic search failed: {e}")
            return SearchResult(content=[], total_found=0, search_time=0.0)

    async def query_facts(self, kb_id: Optional[str] = None, entity: Optional[str] = None,
                         relation: Optional[str] = None, limit: int = 50, **kwargs) -> List[Fact]:
        """Direct call to memory server query facts."""
        try:
            # Handle kb_id parameter by filtering results
            result = await self.memory.query_facts(
                entity=entity, relation=relation, limit=limit
            )

            facts = []
            for fact_data in result.get("facts", []):
                # Apply kb_id filter if specified
                if kb_id and fact_data.get("kb_id") != kb_id:
                    continue

                facts.append(Fact(
                    entity=fact_data.get("entity", ""),
                    relation=fact_data.get("relation", ""),
                    target=fact_data.get("target", ""),
                    confidence=fact_data.get("confidence", 1.0),
                    kb_id=fact_data.get("kb_id"),
                    metadata=fact_data.get("metadata", {})
                ))

            return facts[:limit]  # Apply limit after filtering

        except Exception as e:
            logger.error(f"Direct query facts failed: {e}")
            return []

    async def store_fact(self, entity: str, relation: str, target: str,
                        confidence: float = 1.0, kb_id: Optional[str] = None, **kwargs) -> bool:
        """Direct call to memory server store fact."""
        try:
            result = await self.memory.store_fact(
                entity=entity, relation=relation, target=target,
                confidence=confidence, kb_id=kb_id
            )
            return result.get("ok", False)
        except Exception as e:
            logger.error(f"Direct store fact failed: {e}")
            return False

    async def store_episode(self, request_id: str, messages: List[Dict[str, Any]], **kwargs) -> bool:
        """Direct call to memory server store episode."""
        try:
            result = await self.memory.store_episode(request_id, messages)
            return result.get("ok", False)
        except Exception as e:
            logger.error(f"Direct store episode failed: {e}")
            return False

    async def is_healthy(self) -> bool:
        """Check if direct memory server is accessible."""
        try:
            await self.memory.ensure_connected()
            return self.memory.initialized and not getattr(self.memory, 'memory_unstable', False)
        except Exception:
            return False


class McpMemoryClient(MemoryClient):
    """
    MCP-based memory client that uses tool_mcp_proxy.

    This maintains process isolation and circuit breaker protection,
    but has subprocess overhead.
    """

    def __init__(self, state, server_name: str = "project-memory"):
        self.state = state
        self.server_name = server_name

    async def semantic_search(self, query: str, limit: int = 10, **kwargs) -> SearchResult:
        """MCP proxy call to semantic search."""
        try:
            from agent_runner.tools.mcp import tool_mcp_proxy

            result = await tool_mcp_proxy(
                self.state, self.server_name, "semantic_search",
                {"query": query, "limit": limit},
                bypass_circuit_breaker=kwargs.get("bypass_circuit_breaker", True)
            )

            if result.get("ok"):
                result_obj = result.get("result", {})
                if isinstance(result_obj, str):
                    result_obj = json.loads(result_obj)

                return SearchResult(
                    content=result_obj.get("content", []),
                    total_found=result_obj.get("total_found", 0),
                    search_time=result_obj.get("search_time", 0.0)
                )
            else:
                logger.warning(f"MCP semantic search failed: {result}")
                return SearchResult(content=[], total_found=0, search_time=0.0)

        except Exception as e:
            logger.error(f"MCP semantic search failed: {e}")
            return SearchResult(content=[], total_found=0, search_time=0.0)

    async def query_facts(self, kb_id: Optional[str] = None, entity: Optional[str] = None,
                         relation: Optional[str] = None, limit: int = 50, **kwargs) -> List[Fact]:
        """MCP proxy call to query facts."""
        try:
            from agent_runner.tools.mcp import tool_mcp_proxy

            # Build query parameters
            params = {"limit": limit}
            if kb_id:
                params["kb_id"] = kb_id
            if entity:
                params["entity"] = entity
            if relation:
                params["relation"] = relation

            result = await tool_mcp_proxy(
                self.state, self.server_name, "query_facts", params,
                bypass_circuit_breaker=kwargs.get("bypass_circuit_breaker", True)
            )

            if result.get("ok"):
                result_obj = result.get("result", {})
                if isinstance(result_obj, str):
                    result_obj = json.loads(result_obj)

                facts = []
                for fact_data in result_obj.get("facts", []):
                    facts.append(Fact(
                        entity=fact_data.get("entity", ""),
                        relation=fact_data.get("relation", ""),
                        target=fact_data.get("target", ""),
                        confidence=fact_data.get("confidence", 1.0),
                        kb_id=fact_data.get("kb_id"),
                        metadata=fact_data.get("metadata", {})
                    ))
                return facts
            else:
                logger.warning(f"MCP query facts failed: {result}")
                return []

        except Exception as e:
            logger.error(f"MCP query facts failed: {e}")
            return []

    async def store_fact(self, entity: str, relation: str, target: str,
                        confidence: float = 1.0, kb_id: Optional[str] = None, **kwargs) -> bool:
        """MCP proxy call to store fact."""
        try:
            from agent_runner.tools.mcp import tool_mcp_proxy

            params = {
                "entity": entity,
                "relation": relation,
                "target": target,
                "confidence": confidence
            }
            if kb_id:
                params["kb_id"] = kb_id

            result = await tool_mcp_proxy(
                self.state, self.server_name, "store_fact", params,
                bypass_circuit_breaker=kwargs.get("bypass_circuit_breaker", False)
            )

            return result.get("ok", False)

        except Exception as e:
            logger.error(f"MCP store fact failed: {e}")
            return False

    async def store_episode(self, request_id: str, messages: List[Dict[str, Any]], **kwargs) -> bool:
        """MCP proxy call to store episode."""
        try:
            from agent_runner.tools.mcp import tool_mcp_proxy

            result = await tool_mcp_proxy(
                self.state, self.server_name, "store_episode",
                {"request_id": request_id, "messages": messages},
                bypass_circuit_breaker=kwargs.get("bypass_circuit_breaker", False)
            )

            return result.get("ok", False)

        except Exception as e:
            logger.error(f"MCP store episode failed: {e}")
            return False

    async def is_healthy(self) -> bool:
        """Check if MCP memory server is accessible."""
        try:
            from agent_runner.tools.mcp import tool_mcp_proxy

            result = await tool_mcp_proxy(
                self.state, self.server_name, "check_health", {},
                bypass_circuit_breaker=True
            )

            return result.get("ok", False)

        except Exception:
            return False


def create_memory_client(state, config: Dict[str, Any]) -> MemoryClient:
    """
    Factory function to create the appropriate MemoryClient based on configuration.

    Args:
        state: AgentState instance
        config: Configuration dictionary with 'memory_mode' key

    Returns:
        MemoryClient implementation
    """
    mode = config.get("memory_mode", "direct")

    if mode == "direct":
        if not hasattr(state, 'memory') or state.memory is None:
            raise ValueError("Direct memory mode requires state.memory to be initialized")
        return DirectMemoryClient(state.memory)

    elif mode == "mcp":
        server_name = config.get("memory_mcp_server", "project-memory")
        return McpMemoryClient(state, server_name)

    else:
        raise ValueError(f"Unknown memory mode: {mode}. Supported: 'direct', 'mcp'")