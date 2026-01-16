"""
Memory Query Cache for Phase 4: Vector & Memory Optimizations

Implements intelligent caching of memory system queries (facts, episodes, context)
to reduce database load and improve context retrieval performance.
"""

import hashlib
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import OrderedDict

logger = logging.getLogger("agent_runner.memory_cache")


class MemoryQueryCache:
    """
    Intelligent cache for memory system queries with context-awareness.

    Features:
    - Fact query caching with TTL-based expiration
    - Episode caching for conversation storage
    - Context-aware invalidation
    - Memory-efficient LRU eviction
    - Performance metrics tracking
    """

    def __init__(self, max_cache_size: int = 500, default_ttl: int = 600,
                 enable_metrics: bool = True):
        """
        Initialize the memory query cache.

        Args:
            max_cache_size: Maximum number of cached queries
            default_ttl: Default time-to-live in seconds (10 minutes)
            enable_metrics: Whether to track performance metrics
        """
        self.max_cache_size = max_cache_size
        self.default_ttl = default_ttl
        self.enable_metrics = enable_metrics

        # Cache storage with different TTLs for different data types
        self.fact_cache: OrderedDict[str, Tuple[List[Dict], float, Dict[str, Any]]] = OrderedDict()
        self.episode_cache: OrderedDict[str, Tuple[List[Dict], float, Dict[str, Any]]] = OrderedDict()
        self.context_cache: OrderedDict[str, Tuple[Dict, float, Dict[str, Any]]] = OrderedDict()

        # Custom TTLs for different cache types
        self.ttls = {
            "facts": 600,      # 10 minutes (facts change less frequently)
            "episodes": 300,   # 5 minutes (conversation context)
            "context": 1800,   # 30 minutes (general context)
        }

        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "fact_cache_hits": 0,
            "fact_cache_misses": 0,
            "episode_cache_hits": 0,
            "episode_cache_misses": 0,
            "context_cache_hits": 0,
            "context_cache_misses": 0,
            "evictions": 0,
            "expired_entries": 0,
            "avg_response_time_saved": 0.0
        }

        logger.info(f"MemoryQueryCache initialized: size={max_cache_size}, default_ttl={default_ttl}s")

    def _hash_key(self, *args) -> str:
        """Generate a stable hash key from multiple components."""
        key_input = "|".join(str(arg) for arg in args)
        return hashlib.sha256(key_input.encode('utf-8')).hexdigest()[:16]

    def _is_expired(self, timestamp: float, cache_type: str) -> bool:
        """Check if a cache entry has expired based on cache type."""
        ttl = self.ttls.get(cache_type, self.default_ttl)
        return time.time() - timestamp > ttl

    def _cleanup_expired_entries(self):
        """Remove expired entries from all caches."""
        caches = [
            ("facts", self.fact_cache),
            ("episodes", self.episode_cache),
            ("context", self.context_cache)
        ]

        total_cleaned = 0
        for cache_type, cache in caches:
            expired_keys = []
            for key, (_, timestamp, _) in cache.items():
                if self._is_expired(timestamp, cache_type):
                    expired_keys.append(key)

            for key in expired_keys:
                del cache[key]
                total_cleaned += 1

        if total_cleaned > 0:
            self.metrics["expired_entries"] += total_cleaned
            logger.debug(f"Cleaned up {total_cleaned} expired memory cache entries")

    def _enforce_size_limits(self):
        """Enforce size limits on all caches using LRU eviction."""
        # Calculate total size across all caches
        total_entries = len(self.fact_cache) + len(self.episode_cache) + len(self.context_cache)

        if total_entries <= self.max_cache_size:
            return

        # Need to evict entries - distribute eviction across caches proportionally
        entries_to_evict = total_entries - self.max_cache_size

        # Evict from each cache proportionally
        caches = [
            ("facts", self.fact_cache),
            ("episodes", self.episode_cache),
            ("context", self.context_cache)
        ]

        evicted = 0
        for cache_name, cache in caches:
            if not cache:
                continue

            # Calculate how many to evict from this cache
            cache_ratio = len(cache) / total_entries
            evict_from_cache = max(1, int(entries_to_evict * cache_ratio))

            # Evict LRU entries
            for _ in range(min(evict_from_cache, len(cache))):
                cache.popitem(last=False)  # Remove oldest
                evicted += 1
                self.metrics["evictions"] += 1

        if evicted > 0:
            logger.debug(f"Memory cache LRU eviction: removed {evicted} entries")

    async def query_facts_cached(self, kb_id: str, query: str = "", limit: int = 50) -> List[Dict]:
        """
        Query facts with caching.

        Returns cached results if available and fresh, otherwise performs query and caches.
        """
        if not self.enable_metrics:
            # Fallback to direct query if caching disabled
            return await self._perform_fact_query(kb_id, query, limit)

        self.metrics["total_requests"] += 1
        cache_key = self._hash_key("facts", kb_id, query, limit)

        # Check cache
        if cache_key in self.fact_cache:
            facts, timestamp, metadata = self.fact_cache[cache_key]

            if not self._is_expired(timestamp, "facts"):
                # Cache hit
                self.fact_cache.move_to_end(cache_key)  # Mark as recently used
                self.metrics["fact_cache_hits"] += 1

                # Track response time savings
                if "estimated_savings" in metadata:
                    self._update_avg_savings(metadata["estimated_savings"])

                logger.debug(f"Memory fact cache hit: {cache_key}")
                return facts

            # Expired - remove
            del self.fact_cache[cache_key]

        # Cache miss
        self.metrics["fact_cache_misses"] += 1

        # Perform actual query
        start_time = time.time()
        facts = await self._perform_fact_query(kb_id, query, limit)
        query_time = time.time() - start_time

        # Cache the results
        metadata = {
            "kb_id": kb_id,
            "query": query[:100],  # Truncate for storage
            "limit": limit,
            "result_count": len(facts),
            "estimated_savings": query_time * 0.7,  # Estimate 70% time savings
            "cached_at": time.time()
        }

        self.fact_cache[cache_key] = (facts, time.time(), metadata)
        self.fact_cache.move_to_end(cache_key)

        # Clean up and enforce limits
        self._cleanup_expired_entries()
        self._enforce_size_limits()

        return facts

    async def get_episodes_cached(self, request_id: str) -> List[Dict]:
        """
        Get conversation episodes with caching.
        """
        if not self.enable_metrics:
            return await self._perform_episode_query(request_id)

        cache_key = self._hash_key("episodes", request_id)

        # Check cache
        if cache_key in self.episode_cache:
            episodes, timestamp, metadata = self.episode_cache[cache_key]

            if not self._is_expired(timestamp, "episodes"):
                self.episode_cache.move_to_end(cache_key)
                self.metrics["episode_cache_hits"] += 1
                return episodes

            del self.episode_cache[cache_key]

        # Cache miss
        self.metrics["episode_cache_misses"] += 1

        start_time = time.time()
        episodes = await self._perform_episode_query(request_id)
        query_time = time.time() - start_time

        # Cache results
        metadata = {
            "request_id": request_id,
            "episode_count": len(episodes),
            "estimated_savings": query_time * 0.6,
            "cached_at": time.time()
        }

        self.episode_cache[cache_key] = (episodes, time.time(), metadata)
        self.episode_cache.move_to_end(cache_key)

        self._cleanup_expired_entries()
        self._enforce_size_limits()

        return episodes

    async def get_context_cached(self, context_key: str, context_params: Dict[str, Any] = None) -> Dict:
        """
        Get contextual information with caching.

        Args:
            context_key: Identifier for the context type
            context_params: Parameters that affect the context
        """
        if not self.enable_metrics:
            return await self._perform_context_query(context_key, context_params or {})

        cache_key = self._hash_key("context", context_key, str(sorted(context_params.items())))

        # Check cache
        if cache_key in self.context_cache:
            context, timestamp, metadata = self.context_cache[cache_key]

            if not self._is_expired(timestamp, "context"):
                self.context_cache.move_to_end(cache_key)
                self.metrics["context_cache_hits"] += 1
                return context

            del self.context_cache[cache_key]

        # Cache miss
        self.metrics["context_cache_misses"] += 1

        start_time = time.time()
        context = await self._perform_context_query(context_key, context_params or {})
        query_time = time.time() - start_time

        # Cache results
        metadata = {
            "context_key": context_key,
            "params": context_params,
            "estimated_savings": query_time * 0.8,
            "cached_at": time.time()
        }

        self.context_cache[cache_key] = (context, time.time(), metadata)
        self.context_cache.move_to_end(cache_key)

        self._cleanup_expired_entries()
        self._enforce_size_limits()

        return context

    # Placeholder methods - these would be implemented to interface with actual memory system
    async def _perform_fact_query(self, kb_id: str, query: str, limit: int) -> List[Dict]:
        """Placeholder for actual fact querying logic."""
        # This would interface with the memory server's query_facts method
        logger.debug(f"Performing fact query: kb_id={kb_id}, query='{query}', limit={limit}")
        # Return empty list as placeholder
        return []

    async def _perform_episode_query(self, request_id: str) -> List[Dict]:
        """Placeholder for actual episode querying logic."""
        logger.debug(f"Performing episode query: request_id={request_id}")
        return []

    async def _perform_context_query(self, context_key: str, params: Dict[str, Any]) -> Dict:
        """Placeholder for actual context querying logic."""
        logger.debug(f"Performing context query: key={context_key}, params={params}")
        return {}

    def _update_avg_savings(self, savings: float):
        """Update rolling average of response time savings."""
        current_avg = self.metrics["avg_response_time_saved"]
        total_requests = self.metrics["total_requests"]

        # Simple exponential moving average
        alpha = 0.1  # Smoothing factor
        self.metrics["avg_response_time_saved"] = current_avg * (1 - alpha) + savings * alpha

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        fact_entries = len(self.fact_cache)
        episode_entries = len(self.episode_cache)
        context_entries = len(self.context_cache)
        total_entries = fact_entries + episode_entries + context_entries

        # Calculate hit rates
        total_requests = self.metrics["total_requests"]
        fact_hit_rate = (self.metrics["fact_cache_hits"] /
                        (self.metrics["fact_cache_hits"] + self.metrics["fact_cache_misses"])
                        if (self.metrics["fact_cache_hits"] + self.metrics["fact_cache_misses"]) > 0 else 0)

        episode_hit_rate = (self.metrics["episode_cache_hits"] /
                           (self.metrics["episode_cache_hits"] + self.metrics["episode_cache_misses"])
                           if (self.metrics["episode_cache_hits"] + self.metrics["episode_cache_misses"]) > 0 else 0)

        context_hit_rate = (self.metrics["context_cache_hits"] /
                           (self.metrics["context_cache_hits"] + self.metrics["context_cache_misses"])
                           if (self.metrics["context_cache_hits"] + self.metrics["context_cache_misses"]) > 0 else 0)

        overall_hit_rate = ((self.metrics["fact_cache_hits"] + self.metrics["episode_cache_hits"] + self.metrics["context_cache_hits"]) /
                           total_requests if total_requests > 0 else 0)

        return {
            "total_entries": total_entries,
            "max_entries": self.max_cache_size,
            "fact_cache_entries": fact_entries,
            "episode_cache_entries": episode_entries,
            "context_cache_entries": context_entries,
            "total_requests": total_requests,
            "overall_hit_rate": overall_hit_rate,
            "fact_hit_rate": fact_hit_rate,
            "episode_hit_rate": episode_hit_rate,
            "context_hit_rate": context_hit_rate,
            "evictions": self.metrics["evictions"],
            "expired_entries": self.metrics["expired_entries"],
            "avg_response_time_saved": self.metrics["avg_response_time_saved"],
            "memory_usage_estimate": self._estimate_memory_usage()
        }

    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        base_overhead = 300  # Overhead per entry (larger than vector cache)

        total_bytes = 0
        for cache in [self.fact_cache, self.episode_cache, self.context_cache]:
            for data, _, metadata in cache.values():
                data_size = len(str(data).encode('utf-8'))
                metadata_size = len(str(metadata).encode('utf-8'))
                total_bytes += base_overhead + data_size + metadata_size

        return total_bytes

    def invalidate_by_knowledge_base(self, kb_id: str):
        """Invalidate all cache entries for a specific knowledge base."""
        keys_to_remove = []
        for key, (_, _, metadata) in self.fact_cache.items():
            if metadata.get("kb_id") == kb_id:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.fact_cache[key]

        if keys_to_remove:
            logger.info(f"Invalidated {len(keys_to_remove)} cache entries for KB: {kb_id}")

    def invalidate_by_request(self, request_id: str):
        """Invalidate cache entries related to a specific request."""
        keys_to_remove = []
        for key, (_, _, metadata) in self.episode_cache.items():
            if metadata.get("request_id") == request_id:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.episode_cache[key]

        if keys_to_remove:
            logger.info(f"Invalidated {len(keys_to_remove)} cache entries for request: {request_id}")

    def clear_cache(self):
        """Clear all cached entries."""
        fact_count = len(self.fact_cache)
        episode_count = len(self.episode_cache)
        context_count = len(self.context_cache)

        self.fact_cache.clear()
        self.episode_cache.clear()
        self.context_cache.clear()

        self.metrics = {k: 0 if isinstance(v, (int, float)) else v for k, v in self.metrics.items()}

        logger.info(f"Cleared memory cache: {fact_count} facts, {episode_count} episodes, {context_count} contexts")

    def preload_common_queries(self, common_kb_ids: List[str] = None, common_context_keys: List[str] = None):
        """
        Preload cache with commonly accessed data.

        Args:
            common_kb_ids: Knowledge base IDs to preload
            common_context_keys: Context keys to preload
        """
        if common_kb_ids:
            logger.info(f"Preloading cache with {len(common_kb_ids)} knowledge bases")

        if common_context_keys:
            logger.info(f"Preloading cache with {len(common_context_keys)} context types")

        # Implementation would depend on having access to the memory system
        # This is a placeholder for future preloading logic

    def __len__(self) -> int:
        """Return total number of cached entries."""
        return len(self.fact_cache) + len(self.episode_cache) + len(self.context_cache)