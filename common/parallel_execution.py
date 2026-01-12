"""
Parallel tool execution for agent loops.

Enables concurrent execution of independent tool calls to reduce latency.

Example:
  Sequential: read_file(A) → read_file(B) → read_file(C) = 3 × 100ms = 300ms
  Parallel: [read_file(A), read_file(B), read_file(C)] = 100ms

This addresses "everything feels slow" user feedback.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Represents a single tool call"""
    id: str
    name: str
    arguments: Dict[str, Any]
    
@dataclass
class ToolResult:
    """Result of tool execution"""
    tool_call_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    duration_ms: float = 0.0


class ParallelExecutor:
    """
    Execute multiple tool calls in parallel when safe to do so.
    
    Safety rules:
    - Only parallelize read-only operations
    - Never parallelize writes to same resource  
    - Respect tool dependencies
    - Honor circuit breaker states
    """
    
    # Tool calls that are safe to parallelize
    PARALLELIZABLE_TOOLS = {
        "filesystem_read_file",
        "filesystem_list_directory",
        "filesystem_get_file_info",
        "memory_get_fact",
        "memory_search_facts",
        "web_fetch",  # Multiple URLs
        # Add more read-only tools
    }
    
    # Tools that MUST execute sequentially (writes, state changes)
    SEQUENTIAL_ONLY_TOOLS = {
        "filesystem_write_file",
        "filesystem_create_directory",
        "filesystem_move_file",
        "memory_store_fact",
        "memory_update_fact",
        # Add more stateful tools
    }
    
    def __init__(self, executor, max_parallel: int = 5):
        """
        Args:
            executor: Underlying Executor instance for tool execution
            max_parallel: Maximum concurrent tool executions
        """
        self.executor = executor
        self.max_parallel = max_parallel
        self.semaphore = asyncio.Semaphore(max_parallel)
    
    def can_parallelize(self, tool_calls: List[ToolCall]) -> bool:
        """
        Check if tool calls can be executed in parallel.
        
        Returns True only if:
        - All tools are in PARALLELIZABLE_TOOLS
        - No resource conflicts (e.g., writing to same file)
        - No dependencies between calls
        """
        if len(tool_calls) <= 1:
            return False
        
        # Check if all tools are parallelizable
        for call in tool_calls:
            if call.name in self.SEQUENTIAL_ONLY_TOOLS:
                return False
            if call.name not in self.PARALLELIZABLE_TOOLS:
                # Conservative: don't parallelize unknown tools
                return False
        
        # Check for resource conflicts
        if self._has_resource_conflicts(tool_calls):
            return False
        
        return True
    
    def _has_resource_conflicts(self, tool_calls: List[ToolCall]) -> bool:
        """Detect if tool calls access same resources"""
        # Simple heuristic: check for duplicate file paths in filesystem operations
        filesystem_paths = []
        
        for call in tool_calls:
            if call.name.startswith("filesystem_"):
                path = call.arguments.get("path")
                if path:
                    if path in filesystem_paths:
                        # Duplicate path access
                        return True
                    filesystem_paths.append(path)
        
        return False
    
    async def execute_parallel(
        self,
        tool_calls: List[ToolCall]
    ) -> List[ToolResult]:
        """
        Execute tool calls in parallel.
        
        Args:
            tool_calls: List of tool calls to execute
        
        Returns:
            List of ToolResult in same order as input
        """
        if not self.can_parallelize(tool_calls):
            # Fall back to sequential execution
            logger.debug(f"Cannot parallelize {len(tool_calls)} tool calls - executing sequentially")
            return await self._execute_sequential(tool_calls)
        
        logger.info(f"⚡ Executing {len(tool_calls)} tool calls in PARALLEL")
        
        # Execute with semaphore to limit concurrency
        tasks = [
            self._execute_single_with_semaphore(call)
            for call in tool_calls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for i, (call, result) in enumerate(zip(tool_calls, results)):
            if isinstance(result, Exception):
                final_results.append(ToolResult(
                    tool_call_id=call.id,
                    success=False,
                    result=None,
                    error=str(result)
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def _execute_single_with_semaphore(
        self,
        tool_call: ToolCall
    ) -> ToolResult:
        """Execute single tool call with concurrency limit"""
        async with self.semaphore:
            import time
            start = time.perf_counter()
            
            try:
                # Call underlying executor
                result = await self.executor.execute_tool_call(
                    tool_call.name,
                    tool_call.arguments,
                    tool_call_id=tool_call.id
                )
                
                duration_ms = (time.perf_counter() - start) * 1000
                
                return ToolResult(
                    tool_call_id=tool_call.id,
                    success=True,
                    result=result,
                    duration_ms=duration_ms
                )
                
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                logger.error(f"Tool '{tool_call.name}' failed: {e}")
                
                return ToolResult(
                    tool_call_id=tool_call.id,
                    success=False,
                    result=None,
                    error=str(e),
                    duration_ms=duration_ms
                )
    
    async def _execute_sequential(
        self,
        tool_calls: List[ToolCall]
    ) -> List[ToolResult]:
        """Execute tool calls sequentially (fallback)"""
        results = []
        
        for call in tool_calls:
            result = await self._execute_single_with_semaphore(call)
            results.append(result)
        
        return results
    
    def analyze_execution_plan(
        self,
        tool_calls: List[ToolCall]
    ) -> Dict[str, Any]:
        """
        Analyze tool calls and recommend execution strategy.
        
        Returns:
            {
                "can_parallelize": bool,
                "strategy": "parallel" | "sequential",
                "estimated_speedup": float,
                "reasoning": str
            }
        """
        if len(tool_calls) <= 1:
            return {
                "can_parallelize": False,
                "strategy": "sequential",
                "estimated_speedup": 1.0,
                "reasoning": "Only one tool call"
            }
        
        can_parallel = self.can_parallelize(tool_calls)
        
        if can_parallel:
            # Estimate speedup (simplified)
            # Actual speedup depends on tool latencies
            estimated_speedup = min(len(tool_calls), self.max_parallel)
            
            return {
                "can_parallelize": True,
                "strategy": "parallel",
                "estimated_speedup": estimated_speedup,
                "reasoning": f"All {len(tool_calls)} tools are read-only and independent"
            }
        else:
            # Determine why we can't parallelize
            reasons = []
            
            for call in tool_calls:
                if call.name in self.SEQUENTIAL_ONLY_TOOLS:
                    reasons.append(f"'{call.name}' is write operation")
                elif call.name not in self.PARALLELIZABLE_TOOLS:
                    reasons.append(f"'{call.name}' not in safe list")
            
            if self._has_resource_conflicts(tool_calls):
                reasons.append("Resource conflicts detected")
            
            return {
                "can_parallelize": False,
                "strategy": "sequential",
                "estimated_speedup": 1.0,
                "reasoning": "; ".join(reasons)
            }


class DependencyResolver:
    """
    Resolve dependencies between tool calls to enable partial parallelization.
    
    Example:
      Call A: read_file("input.txt")
      Call B: write_file("output.txt", content=result_of_A)
      Call C: read_file("other.txt")
    
    Strategy: Execute A and C in parallel, then B sequentially.
    """
    
    def __init__(self):
        self.dependency_graph = {}
    
    def build_dependency_graph(
        self,
        tool_calls: List[ToolCall]
    ) -> Dict[str, List[str]]:
        """
        Build dependency graph between tool calls.
        
        Returns:
            {tool_id: [list of tool_ids it depends on]}
        """
        graph = {call.id: [] for call in tool_calls}
        
        # Heuristic: assume sequential tools depend on all previous calls
        # TODO: More sophisticated analysis (e.g., data flow tracking)
        
        for i, call in enumerate(tool_calls):
            if call.name in ParallelExecutor.SEQUENTIAL_ONLY_TOOLS:
                # Depends on all previous calls
                graph[call.id] = [tool_calls[j].id for j in range(i)]
        
        return graph
    
    def get_execution_batches(
        self,
        tool_calls: List[ToolCall]
    ) -> List[List[ToolCall]]:
        """
        Group tool calls into batches that can execute in parallel.
        
        Returns:
            List of batches, where each batch can execute concurrently
        """
        graph = self.build_dependency_graph(tool_calls)
        
        # Simple topological sort into levels
        batches = []
        remaining = set(call.id for call in tool_calls)
        call_map = {call.id: call for call in tool_calls}
        
        while remaining:
            # Find calls with no pending dependencies
            batch = []
            for call_id in list(remaining):
                deps = graph[call_id]
                if all(dep not in remaining for dep in deps):
                    batch.append(call_map[call_id])
            
            if not batch:
                # Circular dependency or error
                logger.error("Cannot resolve tool dependencies!")
                # Fall back to sequential
                return [[call] for call in tool_calls if call.id in remaining]
            
            batches.append(batch)
            for call in batch:
                remaining.remove(call.id)
        
        return batches
