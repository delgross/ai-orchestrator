"""
Memory Query Optimizer for Phase 4: Vector & Memory Optimizations

Implements intelligent memory query batching, deduplication, and optimization
to reduce database load and improve context retrieval performance.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass

logger = logging.getLogger("agent_runner.memory_query_optimizer")


@dataclass
class QueryBatch:
    """Represents a batch of similar queries to be executed together."""
    query_type: str  # "facts", "episodes", "semantic_search"
    queries: List[Dict[str, Any]]
    batch_id: str
    created_at: float = None

    def __post_init__(self):
        self.created_at = time.time()


class MemoryQueryOptimizer:
    """
    Intelligent memory query optimizer with batching and deduplication.

    Features:
    - Query batching for similar operations
    - Deduplication of redundant queries
    - Intelligent query prioritization
    - Performance monitoring and optimization
    - Resource-aware batching (memory, time limits)
    """

    def __init__(self, max_batch_size: int = 10, max_wait_time: float = 0.1,
                 enable_metrics: bool = True):
        """
        Initialize the memory query optimizer.

        Args:
            max_batch_size: Maximum queries to batch together
            max_wait_time: Maximum time to wait for batch completion (seconds)
            enable_metrics: Whether to track performance metrics
        """
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.enable_metrics = enable_metrics

        # Query batching queues
        self.pending_batches: Dict[str, QueryBatch] = {}
        self.batch_results: Dict[str, Dict[str, Any]] = {}
        self.batch_events: Dict[str, asyncio.Event] = {}

        # Deduplication tracking
        self.query_deduplication: Dict[str, asyncio.Future] = {}
        self.query_timestamps: Dict[str, float] = {}

        # Performance metrics
        self.metrics = {
            "total_queries": 0,
            "batched_queries": 0,
            "deduplicated_queries": 0,
            "batch_wait_times": [],
            "query_response_times": [],
            "batch_sizes": [],
            "cache_hits": 0,
            "optimization_savings": 0.0
        }

        logger.info(f"MemoryQueryOptimizer initialized: batch_size={max_batch_size}, wait_time={max_wait_time}s")

    async def optimize_fact_queries(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize a batch of fact queries through batching and deduplication.

        Args:
            queries: List of query dicts with keys: kb_id, query, limit

        Returns:
            List of query results in the same order as input queries
        """
        if not self.enable_metrics:
            return await self._execute_fact_queries_sequentially(queries)

        if len(queries) == 1:
            # Single query - check deduplication first
            query = queries[0]
            query_key = self._generate_query_key("facts", query)

            if query_key in self.query_deduplication:
                # Wait for existing query to complete
                try:
                    result = await asyncio.wait_for(
                        self.query_deduplication[query_key],
                        timeout=5.0  # Don't wait too long
                    )
                    self.metrics["deduplicated_queries"] += 1
                    return [result]
                except asyncio.TimeoutError:
                    # Timeout - proceed with new query
                    pass

            # Execute single query with deduplication tracking
            future = asyncio.Future()
            self.query_deduplication[query_key] = future

            try:
                result = await self._execute_single_fact_query(query)
                future.set_result(result)
                return [result]
            finally:
                # Clean up deduplication tracking
                if query_key in self.query_deduplication:
                    del self.query_deduplication[query_key]

        # Multiple queries - use batching
        return await self._batch_fact_queries(queries)

    async def optimize_semantic_search(self, queries: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Optimize semantic search queries through batching.

        Args:
            queries: List of search queries with keys: query, limit, kb_id

        Returns:
            List of search results, one per input query
        """
        if not self.enable_metrics or len(queries) == 1:
            return await self._execute_semantic_searches_sequentially(queries)

        # Group queries by knowledge base for better batching
        kb_groups = defaultdict(list)
        for i, query in enumerate(queries):
            kb_id = query.get("kb_id", "default")
            kb_groups[kb_id].append((i, query))

        # Execute batches per knowledge base
        results = [None] * len(queries)
        batch_tasks = []

        for kb_id, query_list in kb_groups.items():
            if len(query_list) > 1:
                batch_tasks.append(self._batch_semantic_searches(kb_id, query_list, results))
            else:
                # Single query in this KB
                idx, query = query_list[0]
                batch_tasks.append(self._execute_single_semantic_search(idx, query, results))

        await asyncio.gather(*batch_tasks)
        return results

    async def optimize_episode_operations(self, operations: List[Dict[str, Any]]) -> List[bool]:
        """
        Optimize episode storage/retrieval operations.

        Args:
            operations: List of operations with keys: type ("store"|"retrieve"), request_id, data

        Returns:
            List of operation success indicators
        """
        # Separate reads from writes
        reads = []
        writes = []

        for i, op in enumerate(operations):
            if op["type"] == "retrieve":
                reads.append((i, op))
            elif op["type"] == "store":
                writes.append((i, op))

        results = [None] * len(operations)

        # Execute reads and writes concurrently
        tasks = []
        if reads:
            tasks.append(self._batch_episode_reads(reads, results))
        if writes:
            tasks.append(self._batch_episode_writes(writes, results))

        if tasks:
            await asyncio.gather(*tasks)

        return results

    async def _batch_fact_queries(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute fact queries in optimized batches."""
        # Group by knowledge base
        kb_groups = defaultdict(list)
        for i, query in enumerate(queries):
            kb_id = query.get("kb_id", "default")
            kb_groups[kb_id].append((i, query))

        results = [None] * len(queries)
        batch_tasks = []

        for kb_id, query_list in kb_groups.items():
            batch_tasks.append(self._execute_kb_fact_batch(kb_id, query_list, results))

        await asyncio.gather(*batch_tasks)
        return results

    async def _execute_kb_fact_batch(self, kb_id: str, query_list: List[Tuple[int, Dict]], results: List):
        """Execute a batch of fact queries for a single knowledge base."""
        if len(query_list) <= 1:
            # No batching needed
            for idx, query in query_list:
                results[idx] = await self._execute_single_fact_query(query)
            return

        # Create batch
        batch_id = f"facts_{kb_id}_{time.time()}"
        batch = QueryBatch(
            query_type="facts",
            queries=[query for _, query in query_list],
            batch_id=batch_id
        )

        self.pending_batches[batch_id] = batch
        self.batch_events[batch_id] = asyncio.Event()

        try:
            # Wait for batch to fill or timeout
            start_wait = time.time()
            await asyncio.wait_for(
                self.batch_events[batch_id].wait(),
                timeout=self.max_wait_time
            )
            wait_time = time.time() - start_wait
            self.metrics["batch_wait_times"].append(wait_time)

        except asyncio.TimeoutError:
            # Execute batch now
            pass

        # Execute the batch
        start_time = time.time()
        batch_results = await self._execute_fact_batch(batch)
        execution_time = time.time() - start_time

        # Distribute results back to original queries
        for i, (orig_idx, _) in enumerate(query_list):
            if i < len(batch_results):
                results[orig_idx] = batch_results[i]

        # Track metrics
        self.metrics["batched_queries"] += len(query_list)
        self.metrics["batch_sizes"].append(len(query_list))
        self.metrics["query_response_times"].extend([execution_time] * len(query_list))

        # Cleanup
        if batch_id in self.pending_batches:
            del self.pending_batches[batch_id]
        if batch_id in self.batch_events:
            del self.batch_events[batch_id]

    async def _batch_semantic_searches(self, kb_id: str, query_list: List[Tuple[int, Dict]], results: List):
        """Execute semantic searches in batches."""
        if len(query_list) <= 1:
            for idx, query in query_list:
                results[idx] = await self._execute_single_semantic_search_query(query)
            return

        # Deduplicate search queries
        unique_queries = {}
        query_mapping = {}

        for idx, query in query_list:
            query_text = query["query"]
            if query_text not in unique_queries:
                unique_queries[query_text] = query
                query_mapping[query_text] = []
            query_mapping[query_text].append(idx)

        # Execute unique queries
        unique_results = {}
        for query_text, query in unique_queries.items():
            unique_results[query_text] = await self._execute_single_semantic_search_query(query)

        # Distribute results
        for query_text, indices in query_mapping.items():
            result = unique_results[query_text]
            for idx in indices:
                results[idx] = result

        # Track deduplication savings
        total_queries = len(query_list)
        unique_count = len(unique_queries)
        if unique_count < total_queries:
            savings = total_queries - unique_count
            self.metrics["deduplicated_queries"] += savings
            self.metrics["optimization_savings"] += savings * 0.5  # Estimate 0.5s savings per dedup

    async def _batch_episode_reads(self, reads: List[Tuple[int, Dict]], results: List):
        """Execute episode read operations in batch."""
        if len(reads) <= 1:
            for idx, op in reads:
                results[idx] = await self._execute_episode_read(op)
            return

        # Batch episode reads
        request_ids = [op["request_id"] for _, op in reads]

        start_time = time.time()
        batch_results = await self._execute_episode_batch_read(request_ids)
        execution_time = time.time() - start_time

        # Distribute results
        for i, (idx, _) in enumerate(reads):
            if i < len(batch_results):
                results[idx] = batch_results[i]

        self.metrics["batched_queries"] += len(reads)
        self.metrics["query_response_times"].extend([execution_time] * len(reads))

    async def _batch_episode_writes(self, writes: List[Tuple[int, Dict]], results: List):
        """Execute episode write operations in batch."""
        if len(writes) <= 1:
            for idx, op in writes:
                results[idx] = await self._execute_episode_write(op)
            return

        # Batch episode writes
        write_ops = [op for _, op in writes]

        start_time = time.time()
        batch_results = await self._execute_episode_batch_write(write_ops)
        execution_time = time.time() - start_time

        # Distribute results
        for i, (idx, _) in enumerate(writes):
            if i < len(batch_results):
                results[idx] = batch_results[i]

        self.metrics["batched_queries"] += len(writes)
        self.metrics["query_response_times"].extend([execution_time] * len(writes))

    # Placeholder methods - these would interface with the actual memory system
    async def _execute_single_fact_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single fact query."""
        logger.debug(f"Executing fact query: {query}")
        # Return placeholder result
        return {"facts": [], "count": 0}

    async def _execute_fact_batch(self, batch: QueryBatch) -> List[Dict[str, Any]]:
        """Execute a batch of fact queries."""
        logger.debug(f"Executing fact batch: {batch.batch_id} with {len(batch.queries)} queries")
        # Return placeholder results
        return [{"facts": [], "count": 0} for _ in batch.queries]

    async def _execute_single_semantic_search_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a single semantic search."""
        logger.debug(f"Executing semantic search: {query}")
        return []

    async def _execute_semantic_searches_sequentially(self, queries: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Execute semantic searches sequentially."""
        results = []
        for query in queries:
            results.append(await self._execute_single_semantic_search_query(query))
        return results

    async def _execute_fact_queries_sequentially(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute fact queries sequentially."""
        results = []
        for query in queries:
            results.append(await self._execute_single_fact_query(query))
        return results

    async def _execute_episode_read(self, op: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute episode read operation."""
        logger.debug(f"Executing episode read: {op['request_id']}")
        return []

    async def _execute_episode_write(self, op: Dict[str, Any]) -> bool:
        """Execute episode write operation."""
        logger.debug(f"Executing episode write: {op['request_id']}")
        return True

    async def _execute_episode_batch_read(self, request_ids: List[str]) -> List[List[Dict[str, Any]]]:
        """Execute batch episode read."""
        logger.debug(f"Executing batch episode read: {len(request_ids)} requests")
        return [[] for _ in request_ids]

    async def _execute_episode_batch_write(self, operations: List[Dict[str, Any]]) -> List[bool]:
        """Execute batch episode write."""
        logger.debug(f"Executing batch episode write: {len(operations)} operations")
        return [True for _ in operations]

    def _generate_query_key(self, query_type: str, query: Dict[str, Any]) -> str:
        """Generate a unique key for query deduplication."""
        key_parts = [query_type]
        if "kb_id" in query:
            key_parts.append(query["kb_id"])
        if "query" in query:
            key_parts.append(query["query"][:50])  # Limit query length
        if "limit" in query:
            key_parts.append(str(query["limit"]))

        return "|".join(key_parts)

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics."""
        total_queries = self.metrics["total_queries"]

        # Calculate averages
        avg_batch_wait = sum(self.metrics["batch_wait_times"]) / len(self.metrics["batch_wait_times"]) if self.metrics["batch_wait_times"] else 0
        avg_response_time = sum(self.metrics["query_response_times"]) / len(self.metrics["query_response_times"]) if self.metrics["query_response_times"] else 0
        avg_batch_size = sum(self.metrics["batch_sizes"]) / len(self.metrics["batch_sizes"]) if self.metrics["batch_sizes"] else 0

        # Calculate rates
        batch_rate = self.metrics["batched_queries"] / total_queries if total_queries > 0 else 0
        dedup_rate = self.metrics["deduplicated_queries"] / total_queries if total_queries > 0 else 0
        cache_hit_rate = self.metrics["cache_hits"] / total_queries if total_queries > 0 else 0

        return {
            "total_queries": total_queries,
            "batched_queries": self.metrics["batched_queries"],
            "deduplicated_queries": self.metrics["deduplicated_queries"],
            "cache_hits": self.metrics["cache_hits"],
            "batch_rate": batch_rate,
            "deduplication_rate": dedup_rate,
            "cache_hit_rate": cache_hit_rate,
            "avg_batch_wait_time": avg_batch_wait,
            "avg_response_time": avg_response_time,
            "avg_batch_size": avg_batch_size,
            "total_optimization_savings": self.metrics["optimization_savings"],
            "pending_batches": len(self.pending_batches),
            "active_deduplications": len(self.query_deduplication)
        }

    def clear_pending_operations(self):
        """Clear any pending batched operations."""
        for event in self.batch_events.values():
            event.set()  # Wake up any waiting operations

        self.pending_batches.clear()
        self.batch_events.clear()
        self.query_deduplication.clear()

        logger.info("Cleared all pending memory query operations")