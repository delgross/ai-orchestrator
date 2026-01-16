"""
Vector Search Cache for Phase 4: Vector & Memory Optimizations

Implements intelligent caching of vector-based tool searches to dramatically
reduce database load and improve tool suggestion response times.
"""

import hashlib
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import OrderedDict

logger = logging.getLogger("agent_runner.vector_search_cache")


class VectorSearchCache:
    """
    Cache for vector-based tool searches with LRU eviction and TTL management.

    Key Features:
    - Query-based caching with hash keys
    - TTL (Time-To-Live) expiration
    - LRU (Least Recently Used) eviction
    - Hit rate tracking and performance metrics
    - Memory-efficient storage
    """

    def __init__(self, max_cache_size: int = 200, ttl_seconds: int = 300,
                 enable_metrics: bool = True):
        """
        Initialize the vector search cache.

        Args:
            max_cache_size: Maximum number of cached queries
            ttl_seconds: Time-to-live for cache entries (5 minutes default)
            enable_metrics: Whether to track performance metrics
        """
        self.max_cache_size = max_cache_size
        self.ttl_seconds = ttl_seconds
        self.enable_metrics = enable_metrics

        # Cache storage: query_hash -> (results, timestamp, hit_count, metadata)
        self.cache: OrderedDict[str, Tuple[List[Dict], float, int, Dict[str, Any]]] = OrderedDict()

        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "evictions": 0,
            "expired_entries": 0,
            "hit_rate": 0.0,
            "avg_response_time_saved": 0.0
        }

        # Response time tracking for hit rate calculation
        self.response_times = []

        logger.info(f"VectorSearchCache initialized: size={max_cache_size}, ttl={ttl_seconds}s")

    def _hash_query(self, query: str, limit: int = 8, **kwargs) -> str:
        """
        Generate a stable hash for the query and parameters.

        Includes query text, limit, and any additional parameters that affect results.
        """
        # Sort kwargs for consistent hashing
        sorted_kwargs = sorted(kwargs.items()) if kwargs else []

        # Create hash input
        hash_input = f"{query}|{limit}|{sorted_kwargs}"
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()[:16]

    def _is_expired(self, timestamp: float) -> bool:
        """Check if a cache entry has expired."""
        return time.time() - timestamp > self.ttl_seconds

    def _cleanup_expired_entries(self):
        """Remove expired cache entries."""
        expired_keys = []
        for key, (_, timestamp, _, _) in self.cache.items():
            if self._is_expired(timestamp):
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]
            self.metrics["expired_entries"] += 1

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired vector cache entries")

    def _enforce_size_limit(self):
        """Enforce cache size limit using LRU eviction."""
        while len(self.cache) > self.max_cache_size:
            # Remove least recently used (first item in OrderedDict)
            evicted_key, (_, _, _, _) = self.cache.popitem(last=False)
            self.metrics["evictions"] += 1
            logger.debug(f"LRU eviction: removed {evicted_key}")

    def get_cached_results(self, query: str, limit: int = 8, **kwargs) -> Optional[List[Dict]]:
        """
        Get cached vector search results if available and fresh.

        Returns None if no valid cache entry exists (cache miss).
        """
        if not self.enable_metrics:
            return None

        self.metrics["total_requests"] += 1
        query_hash = self._hash_query(query, limit, **kwargs)

        if query_hash in self.cache:
            results, timestamp, hit_count, metadata = self.cache[query_hash]

            # Check if expired
            if self._is_expired(timestamp):
                del self.cache[query_hash]
                self.metrics["expired_entries"] += 1
                logger.debug(f"Cache expired for query: {query_hash}")
                return None

            # Cache hit - update access patterns
            new_hit_count = hit_count + 1
            self.cache[query_hash] = (results, timestamp, new_hit_count, metadata)
            self.cache.move_to_end(query_hash)  # Mark as most recently used

            self.metrics["cache_hits"] += 1

            # Track response time savings (estimated)
            if "estimated_savings" in metadata:
                self.response_times.append(metadata["estimated_savings"])

            logger.debug(f"Vector cache hit: {query_hash} (hit #{new_hit_count})")
            return results

        # Cache miss
        self.metrics["cache_misses"] += 1
        return None

    def store_results(self, query: str, results: List[Dict], limit: int = 8,
                     estimated_savings: float = 0.0, **kwargs):
        """
        Store vector search results in cache.

        Args:
            query: The search query
            results: The search results to cache
            limit: The result limit used in search
            estimated_savings: Estimated time saved by caching (for metrics)
            **kwargs: Additional search parameters
        """
        if not self.enable_metrics:
            return

        query_hash = self._hash_query(query, limit, **kwargs)

        # Clean up expired entries first
        self._cleanup_expired_entries()

        # Store new entry
        metadata = {
            "query": query[:100],  # Truncate for storage
            "limit": limit,
            "result_count": len(results),
            "estimated_savings": estimated_savings,
            "cached_at": time.time()
        }

        self.cache[query_hash] = (results, time.time(), 0, metadata)
        self.cache.move_to_end(query_hash)  # Mark as most recently used

        # Enforce size limit
        self._enforce_size_limit()

        logger.debug(f"Cached vector search results: {query_hash} ({len(results)} results)")

    async def get_or_search(self, query: str, search_function, limit: int = 8, **kwargs):
        """
        Get cached results or perform fresh search with automatic caching.

        Args:
            query: The search query
            search_function: Async function to perform actual search
            limit: Result limit
            **kwargs: Additional search parameters

        Returns:
            Search results (from cache or fresh search)
        """
        # Try cache first
        cached_results = self.get_cached_results(query, limit, **kwargs)
        if cached_results is not None:
            return cached_results

        # Cache miss - perform actual search
        start_time = time.time()
        try:
            results = await search_function(query, limit=limit, **kwargs)
            search_time = time.time() - start_time

            # Estimate time saved by caching (rough heuristic)
            estimated_savings = search_time * 0.8  # Assume 80% of time is saved by caching

            # Cache the results
            self.store_results(query, results, limit, estimated_savings, **kwargs)

            return results

        except Exception as e:
            logger.warning(f"Vector search failed for query '{query}': {e}")
            # Return empty results on failure (don't cache failures)
            return []

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        total_entries = len(self.cache)

        if total_entries > 0:
            avg_age = sum(time.time() - ts for _, ts, _, _ in self.cache.values()) / total_entries
            total_hits = sum(hits for _, _, hits, _ in self.cache.values())
            avg_hits = total_hits / total_entries
        else:
            avg_age = 0
            total_hits = 0
            avg_hits = 0

        # Calculate hit rate
        if self.metrics["total_requests"] > 0:
            hit_rate = self.metrics["cache_hits"] / self.metrics["total_requests"]
        else:
            hit_rate = 0.0

        # Calculate average response time savings
        if self.response_times:
            avg_savings = sum(self.response_times) / len(self.response_times)
        else:
            avg_savings = 0.0

        return {
            "total_entries": total_entries,
            "max_entries": self.max_cache_size,
            "hit_rate": hit_rate,
            "total_requests": self.metrics["total_requests"],
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "evictions": self.metrics["evictions"],
            "expired_entries": self.metrics["expired_entries"],
            "average_entry_age": avg_age,
            "average_hits_per_entry": avg_hits,
            "total_hit_count": total_hits,
            "average_time_saved_per_hit": avg_savings,
            "memory_usage_estimate": self._estimate_memory_usage()
        }

    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage of cache in bytes."""
        base_overhead = 200  # Overhead per entry
        total_bytes = 0

        for results, _, _, metadata in self.cache.values():
            # Estimate size of results (rough approximation)
            results_size = len(str(results).encode('utf-8'))
            metadata_size = len(str(metadata).encode('utf-8'))
            total_bytes += base_overhead + results_size + metadata_size

        return total_bytes

    def clear_cache(self):
        """Clear all cached entries."""
        count = len(self.cache)
        self.cache.clear()
        self.metrics = {k: 0 for k in self.metrics.keys()}
        self.response_times.clear()
        logger.info(f"Cleared vector search cache ({count} entries)")

    def get_popular_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular cached queries by hit count."""
        popular = []

        for query_hash, (_, _, hits, metadata) in self.cache.items():
            popular.append({
                "query_hash": query_hash,
                "query_preview": metadata.get("query", "")[:50],
                "hits": hits,
                "result_count": metadata.get("result_count", 0),
                "estimated_savings": metadata.get("estimated_savings", 0)
            })

        # Sort by hits descending
        popular.sort(key=lambda x: x["hits"], reverse=True)
        return popular[:limit]

    def preload_common_queries(self, common_queries: List[str]):
        """
        Preload cache with common queries to warm up the cache.

        Args:
            common_queries: List of common search queries to cache
        """
        logger.info(f"Preloading cache with {len(common_queries)} common queries")
        # Note: This would be called during system initialization
        # Actual implementation would depend on having access to the vector store

    def __len__(self) -> int:
        """Return number of cached entries."""
        return len(self.cache)

    def __contains__(self, query_hash: str) -> bool:
        """Check if a query hash is in cache."""
        return query_hash in self.cache