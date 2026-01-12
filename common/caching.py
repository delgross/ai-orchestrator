"""
Aggressive multi-layer caching system for performance optimization.

Implements Phase 2 caching strategy:
- MCP tool response caching (deterministic operations)
- LLM response caching (identical prompts)
- Embedding caching (reduce RAG latency)
- Tool metadata caching (reduce discovery overhead)
"""
import hashlib
import json
import time
import logging
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache invalidation strategies"""
    TTL = "ttl"  # Time-to-live
    LRU = "lru"  # Least recently used
    MANUAL = "manual"  # Explicit invalidation only


@dataclass
class CacheEntry:
    """Cached value with metadata"""
    value: Any
    created_at: float
    access_count: int = 0
    last_accessed: float = 0.0
    ttl_seconds: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if entry is expired based on TTL"""
        if self.ttl_seconds is None:
            return False
        return (time.time() - self.created_at) > self.ttl_seconds
    
    def touch(self):
        """Update access metadata"""
        self.access_count += 1
        self.last_accessed = time.time()


class MultiLayerCache:
    """
    High-performance multi-layer cache with configurable strategies.
    
    Features:
    - TTL expiration
    - LRU eviction
    - Size limits
    - Hit/miss metrics
    - Namespace isolation
    """
    
    def __init__(
        self,
        max_size: int = 10000,
        default_ttl: Optional[float] = 3600.0,  # 1 hour
        strategy: CacheStrategy = CacheStrategy.LRU
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
    def _make_key(self, namespace: str, key: str) -> str:
        """Create namespaced cache key"""
        return f"{namespace}:{key}"
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """Retrieve cached value"""
        cache_key = self._make_key(namespace, key)
        
        if cache_key not in self._cache:
            self.misses += 1
            return None
        
        entry = self._cache[cache_key]
        
        # Check expiration
        if entry.is_expired():
            del self._cache[cache_key]
            self.misses += 1
            return None
        
        # Update access metadata
        entry.touch()
        
        # Move to end for LRU
        if self.strategy == CacheStrategy.LRU:
            self._cache.move_to_end(cache_key)
        
        self.hits += 1
        return entry.value
    
    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[float] = None
    ) -> None:
        """Store value in cache"""
        cache_key = self._make_key(namespace, key)
        
        # Use default TTL if not specified
        if ttl is None:
            ttl = self.default_ttl
        
        entry = CacheEntry(
            value=value,
            created_at=time.time(),
            ttl_seconds=ttl
        )
        
        self._cache[cache_key] = entry
        
        # Enforce size limit with LRU eviction
        if len(self._cache) > self.max_size:
            # Remove oldest entry (FIFO if not LRU strategy)
            evicted_key, _ = self._cache.popitem(last=False)
            self.evictions += 1
            logger.debug(f"Evicted cache entry: {evicted_key}")
    
    def invalidate(self, namespace: str, key: Optional[str] = None) -> int:
        """
        Invalidate cache entries.
        
        Args:
            namespace: Namespace to invalidate
            key: Specific key, or None to invalidate entire namespace
        
        Returns:
            Number of entries invalidated
        """
        if key is not None:
            # Invalidate specific key
            cache_key = self._make_key(namespace, key)
            if cache_key in self._cache:
                del self._cache[cache_key]
                return 1
            return 0
        else:
            # Invalidate entire namespace
            prefix = f"{namespace}:"
            keys_to_delete = [
                k for k in self._cache.keys()
                if k.startswith(prefix)
            ]
            for k in keys_to_delete:
                del self._cache[k]
            return len(keys_to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self.hits = 0
        self.misses = 0
        self.evictions = 0


class MCPToolCache:
    """
    Specialized cache for MCP tool responses.
    
    Caches deterministic tool calls (e.g., read_file with same path).
    Does NOT cache non-deterministic calls (e.g., current_time).
    """
    
    # Tools that are safe to cache (deterministic operations)
    CACHEABLE_TOOLS = {
        "filesystem_read_file",
        "filesystem_list_directory", 
        "memory_get_fact",
        "memory_search_facts",
        # Add more deterministic tools
    }
    
    # Tools that should NEVER be cached
    UNCACHEABLE_TOOLS = {
        "time_current_time",
        "web_search",
        "web_fetch",
        # Add more non-deterministic tools
    }
    
    def __init__(self, underlying_cache: MultiLayerCache):
        self.cache = underlying_cache
        self.namespace = "mcp_tools"
    
    def _hash_args(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Create deterministic hash of tool call"""
        # Serialize arguments to JSON (sorted keys for consistency)
        args_str = json.dumps(arguments, sort_keys=True)
        content = f"{tool_name}:{args_str}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def is_cacheable(self, tool_name: str) -> bool:
        """Check if tool results can be cached"""
        if tool_name in self.UNCACHEABLE_TOOLS:
            return False
        if tool_name in self.CACHEABLE_TOOLS:
            return True
        # Default: cache filesystem/memory tools, don't cache others
        return tool_name.startswith(("filesystem_", "memory_"))
    
    async def get_or_execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        executor_func,
        ttl: float = 300.0  # 5 minutes default
    ) -> Any:
        """
        Get cached result or execute tool and cache result.
        
        Args:
            tool_name: Name of MCP tool
            arguments: Tool arguments
            executor_func: Async function to execute if cache miss
            ttl: Cache TTL in seconds
        
        Returns:
            Tool execution result
        """
        if not self.is_cacheable(tool_name):
            # Execute without caching
            return await executor_func()
        
        # Check cache
        cache_key = self._hash_args(tool_name, arguments)
        cached_result = self.cache.get(self.namespace, cache_key)
        
        if cached_result is not None:
            logger.debug(f"Cache HIT: {tool_name} with {arguments}")
            return cached_result
        
        # Cache miss - execute and store
        logger.debug(f"Cache MISS: {tool_name} with {arguments}")
        result = await executor_func()
        
        self.cache.set(self.namespace, cache_key, result, ttl=ttl)
        return result


class LLMResponseCache:
    """
    Cache for LLM responses to identical prompts.
    
    WARNING: Use carefully - only cache when:
    - Temperature = 0 (deterministic)
    - Prompt is identical
    - Model is same
    - No streaming (or cache full response)
    """
    
    def __init__(self, underlying_cache: MultiLayerCache):
        self.cache = underlying_cache
        self.namespace = "llm_responses"
    
    def _hash_request(
        self,
        model: str,
        messages: list,
        temperature: float,
        **kwargs
    ) -> str:
        """Create hash of LLM request"""
        # Only cache if temperature=0 (deterministic)
        if temperature != 0.0:
            return None
        
        content = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }, sort_keys=True)
        
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get_or_call(
        self,
        model: str,
        messages: list,
        temperature: float,
        llm_func,
        ttl: float = 1800.0,  # 30 minutes
        **kwargs
    ) -> Any:
        """Get cached response or call LLM"""
        # Generate cache key
        cache_key = self._hash_request(model, messages, temperature, **kwargs)
        
        if cache_key is None:
            # Non-deterministic request, don't cache
            return await llm_func()
        
        # Check cache
        cached_response = self.cache.get(self.namespace, cache_key)
        if cached_response is not None:
            logger.debug(f"LLM Cache HIT: {model} with {len(messages)} messages")
            return cached_response
        
        # Cache miss
        logger.debug(f"LLM Cache MISS: {model} with {len(messages)} messages")
        response = await llm_func()
        
        self.cache.set(self.namespace, cache_key, response, ttl=ttl)
        return response


class EmbeddingCache:
    """
    Cache for text embeddings (expensive to compute).
    
    Reduces RAG latency by caching embedding vectors.
    """
    
    def __init__(self, underlying_cache: MultiLayerCache):
        self.cache = underlying_cache
        self.namespace = "embeddings"
    
    def _hash_text(self, text: str, model: str) -> str:
        """Create hash of text + model"""
        content = f"{model}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get_or_compute(
        self,
        text: str,
        model: str,
        compute_func,
        ttl: float = 3600.0  # 1 hour
    ) -> list:
        """Get cached embedding or compute"""
        cache_key = self._hash_text(text, model)
        
        # Check cache
        cached_embedding = self.cache.get(self.namespace, cache_key)
        if cached_embedding is not None:
            return cached_embedding
        
        # Compute embedding
        embedding = await compute_func()
        
        self.cache.set(self.namespace, cache_key, embedding, ttl=ttl)
        return embedding


# Global cache instance (initialized by state)
_global_cache: Optional[MultiLayerCache] = None


def get_cache() -> MultiLayerCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiLayerCache(
            max_size=10000,
            default_ttl=3600.0,
            strategy=CacheStrategy.LRU
        )
    return _global_cache


def get_mcp_cache() -> MCPToolCache:
    """Get MCP tool cache"""
    return MCPToolCache(get_cache())


def get_llm_cache() -> LLMResponseCache:
    """Get LLM response cache"""
    return LLMResponseCache(get_cache())


def get_embedding_cache() -> EmbeddingCache:
    """Get embedding cache"""
    return EmbeddingCache(get_cache())
