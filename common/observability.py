"""
Comprehensive Observability System

This module provides:
- Request lifecycle tracking with detailed timestamps
- Performance metrics at every stage
- Component health monitoring
- Resource usage tracking
- Error tracking with full context
- Data export for analysis
- Real-time monitoring endpoints
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger("observability")


class RequestStage(Enum):
    """Stages in a request lifecycle."""
    RECEIVED = "received"
    AUTH_CHECKED = "auth_checked"
    PARSED = "parsed"
    ROUTING_DECIDED = "routing_decided"
    UPSTREAM_CALL_START = "upstream_call_start"
    UPSTREAM_CALL_END = "upstream_call_end"
    PROCESSING = "processing"
    RESPONSE_SENT = "response_sent"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"


class ComponentType(Enum):
    """Types of system components."""
    ROUTER = "router"
    AGENT_RUNNER = "agent_runner"
    MCP_SERVER = "mcp_server"
    PROVIDER = "provider"
    DATABASE = "database"
    CACHE = "cache"


@dataclass
class PerformanceMetric:
    """A single performance measurement."""
    timestamp: float
    component: str
    operation: str
    duration_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None


@dataclass
class RequestLifecycle:
    """Complete lifecycle tracking for a single request."""
    request_id: str
    method: str
    path: str
    stage: RequestStage
    stages: Dict[str, float] = field(default_factory=dict)  # stage -> timestamp
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: List[PerformanceMetric] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    duration_ms: Optional[float] = None
    
    def record_stage(self, stage: RequestStage, metadata: Optional[Dict[str, Any]] = None):
        """Record a stage transition."""
        self.stage = stage
        self.stages[stage.value] = time.time()
        if metadata:
            self.metadata.update(metadata)
    
    def add_metric(self, component: str, operation: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None):
        """Add a performance metric."""
        self.performance_metrics.append(PerformanceMetric(
            timestamp=time.time(),
            component=component,
            operation=operation,
            duration_ms=duration_ms,
            metadata=metadata or {},
            request_id=self.request_id
        ))
    
    def record_stage_duration(self, stage: str, duration_ms: float):
        """Record duration for a specific stage (for efficiency analysis)."""
        # This will be used by observability system to track stage durations
        pass  # Implementation in ObservabilitySystem
    
    def add_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Record an error."""
        self.errors.append({
            "timestamp": time.time(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        })
        self.record_stage(RequestStage.ERROR, {"error": str(error)})
    
    def complete(self):
        """Mark request as completed."""
        self.completed_at = time.time()
        self.duration_ms = (self.completed_at - self.started_at) * 1000
        if self.stage != RequestStage.ERROR:
            self.record_stage(RequestStage.COMPLETED)


@dataclass
class ComponentHealth:
    """Health status of a component."""
    component_type: ComponentType
    component_id: str
    status: str  # "healthy", "degraded", "unhealthy", "unknown"
    last_check: float
    response_time_ms: Optional[float] = None
    error_count: int = 0
    success_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EfficiencyMetrics:
    """Efficiency and throughput metrics."""
    requests_per_second: float = 0.0
    tokens_per_second: float = 0.0
    cache_hit_rate: float = 0.0
    connection_pool_utilization: float = 0.0
    semaphore_wait_time_avg_ms: float = 0.0
    queue_depth: int = 0
    time_breakdown: Dict[str, float] = field(default_factory=dict)  # stage -> avg_ms
    network_bytes_sent: int = 0
    network_bytes_received: int = 0
    avg_request_size_bytes: int = 0
    avg_response_size_bytes: int = 0


@dataclass
class SystemMetrics:
    """Aggregated system metrics."""
    timestamp: float
    active_requests: int
    completed_requests_1min: int
    error_rate_1min: float
    avg_response_time_1min: float
    component_health: Dict[str, ComponentHealth]
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    efficiency: EfficiencyMetrics = field(default_factory=EfficiencyMetrics)


class ObservabilitySystem:
    """
    Comprehensive observability and monitoring system.
    
    Designed to be extensible for future capabilities:
    - Anomaly detection integration
    - Learning system integration
    - Automated remediation integration
    - Experimentation framework integration
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        max_active_requests: int = 1000,
        max_completed_requests: int = 10000,
        max_performance_metrics: int = 50000,
        max_errors: int = 1000,
        max_metrics_history: int = 1000,
    ):
        """
        Initialize observability system with configurable limits.
        
        Args:
            storage_path: Path for data export
            max_active_requests: Maximum active requests to track
            max_completed_requests: Maximum completed requests to keep
            max_performance_metrics: Maximum performance metrics to keep
            max_errors: Maximum errors to keep
            max_metrics_history: Maximum system metrics snapshots to keep
        """
        if storage_path is None:
            storage_path = Path(__file__).parent.parent / "logs" / "observability"
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Active request tracking
        self.active_requests: Dict[str, RequestLifecycle] = {}
        self.max_active_requests = max_active_requests
        
        # Completed requests (for analysis)
        self.completed_requests: deque = deque(maxlen=max_completed_requests)
        
        # Performance metrics
        self.performance_metrics: deque = deque(maxlen=max_performance_metrics)
        
        # Component health tracking
        self.component_health: Dict[str, ComponentHealth] = {}
        
        # Error tracking
        self.recent_errors: deque = deque(maxlen=max_errors)
        
        # Aggregated metrics
        self.system_metrics_history: deque = deque(maxlen=max_metrics_history)
        
        # Request counters (for rate calculations)
        self.request_counters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=60))  # 1 minute windows
        
        # Efficiency tracking
        self.semaphore_wait_times: deque = deque(maxlen=1000)  # Track wait times for concurrency slots
        self.stage_durations: Dict[str, deque] = defaultdict(lambda: deque(maxlen=5000))  # stage -> durations
        self.request_sizes: deque = deque(maxlen=1000)  # Request body sizes in bytes
        self.response_sizes: deque = deque(maxlen=1000)  # Response sizes in bytes
        self.network_bytes_sent: int = 0
        self.network_bytes_received: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.connection_reuses: int = 0
        self.connection_creates: int = 0
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        # Extension points for future capabilities
        # Initialize anomaly detector automatically
        try:
            from common.anomaly_detector import AnomalyDetector
            self.anomaly_detector: Optional[AnomalyDetector] = AnomalyDetector()
            logger.info("Anomaly detector initialized and integrated")
        except ImportError:
            self.anomaly_detector = None
            logger.warning("Anomaly detector not available")
        
        self.learning_system: Optional[Any] = None  # Will be set by learning system
        self.remediation_engine: Optional[Any] = None  # Will be set by remediation system
        self.experimentation_framework: Optional[Any] = None  # Will be set by experimentation system
    
    async def start_request(self, request_id: str, method: str, path: str, metadata: Optional[Dict[str, Any]] = None) -> RequestLifecycle:
        """Start tracking a new request."""
        async with self._lock:
            lifecycle = RequestLifecycle(
                request_id=request_id,
                method=method,
                path=path,
                stage=RequestStage.RECEIVED,
                metadata=metadata or {}
            )
            lifecycle.record_stage(RequestStage.RECEIVED)
            
            # Clean up old requests if we're at capacity - use efficient O(n) approach
            if len(self.active_requests) >= self.max_active_requests:
                # Find oldest requests without full sort - O(n) instead of O(n log n)
                # Use min() to find oldest, repeat for 10% removal
                to_remove_count = self.max_active_requests // 10
                to_remove = []
                # Create list of (started_at, req_id) tuples for efficient min finding
                request_ages = [(req.started_at, req_id) for req_id, req in self.active_requests.items()]
                # Remove oldest requests efficiently
                for _ in range(to_remove_count):
                    if request_ages:
                        oldest = min(request_ages, key=lambda x: x[0])
                        request_ages.remove(oldest)
                        to_remove.append(oldest[1])
                
                for req_id in to_remove:
                    req = self.active_requests.pop(req_id, None)
                    if req:
                        req.record_stage(RequestStage.TIMEOUT, {"reason": "capacity_limit"})
                        self.completed_requests.append(req)
            
            self.active_requests[request_id] = lifecycle
            self._increment_counter("requests_total")
            return lifecycle
    
    async def get_request(self, request_id: str) -> Optional[RequestLifecycle]:
        """Get an active request by ID."""
        async with self._lock:
            return self.active_requests.get(request_id)
    
    async def complete_request(self, request_id: str):
        """Mark a request as completed."""
        async with self._lock:
            lifecycle = self.active_requests.pop(request_id, None)
            if lifecycle:
                lifecycle.complete()
                self.completed_requests.append(lifecycle)
                
                # Add all performance metrics to global collection
                # Use extend for efficiency instead of append in loop
                if lifecycle.performance_metrics:
                    self.performance_metrics.extend(lifecycle.performance_metrics)
                
                # Track stage durations for efficiency analysis
                if lifecycle.stages and len(lifecycle.stages) > 1:
                    stage_times = sorted(lifecycle.stages.items(), key=lambda x: x[1])
                    for i in range(len(stage_times) - 1):
                        stage_name = stage_times[i][0]
                        duration_ms = (stage_times[i + 1][1] - stage_times[i][1]) * 1000
                        self.stage_durations[stage_name].append(duration_ms)
                
                # Track errors
                if lifecycle.errors:
                    error_records = [{"request_id": request_id, **error} for error in lifecycle.errors]
                    self.recent_errors.extend(error_records)
                
                # Update counters
                self._increment_counter("requests_completed")
                if lifecycle.stage == RequestStage.ERROR:
                    self._increment_counter("requests_errors")
    
    async def record_component_health(
        self,
        component_type: ComponentType,
        component_id: str,
        status: str,
        response_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record component health check."""
        async with self._lock:
            key = f"{component_type.value}:{component_id}"
            health = self.component_health.get(key)
            
            if not health:
                health = ComponentHealth(
                    component_type=component_type,
                    component_id=component_id,
                    status=status,
                    last_check=time.time(),
                    response_time_ms=response_time_ms,
                    metadata=metadata or {}
                )
            else:
                health.status = status
                health.last_check = time.time()
                health.response_time_ms = response_time_ms
                if metadata:
                    health.metadata.update(metadata)
            
            if status == "healthy":
                health.success_count += 1
            else:
                health.error_count += 1
            
            self.component_health[key] = health
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics snapshot."""
        now = time.time()
        one_minute_ago = now - 60
        
        # Optimize: Only iterate through deque once, use early exit for old requests
        # Since deque is ordered (newest last), iterate backwards for efficiency
        async with self._lock:
            # Use single pass to calculate metrics
            completed_count = 0
            error_count = 0
            response_time_sum = 0.0
            response_time_count = 0
            
            # Iterate backwards (newest first) - can exit early when we hit old requests
            for r in reversed(self.completed_requests):
                if not r.completed_at or r.completed_at < one_minute_ago:
                    break  # All older requests are older than 1 minute
                
                completed_count += 1
                if r.stage == RequestStage.ERROR:
                    error_count += 1
                if r.duration_ms:
                    response_time_sum += r.duration_ms
                    response_time_count += 1
            
            error_rate = error_count / max(completed_count, 1)
            avg_response_time = response_time_sum / response_time_count if response_time_count > 0 else 0.0
            
            # Extract token counts from metadata for throughput calculation
            total_tokens = 0
            for r in reversed(self.completed_requests):
                if not r.completed_at or r.completed_at < one_minute_ago:
                    break
                if r.metadata:
                    usage = r.metadata.get("usage", {})
                    if isinstance(usage, dict):
                        total_tokens += usage.get("total_tokens", 0)
            
            # Calculate efficiency metrics
            efficiency = self._calculate_efficiency_metrics(completed_count, total_tokens)
            
            # Get resource usage (if available) - do this outside lock
            resource_usage = self._get_resource_usage()
            
            metrics = SystemMetrics(
                timestamp=now,
                active_requests=len(self.active_requests),
                completed_requests_1min=completed_count,
                error_rate_1min=error_rate,
                avg_response_time_1min=avg_response_time,
                component_health=self.component_health.copy(),
                resource_usage=resource_usage,
                efficiency=efficiency
            )
            
            self.system_metrics_history.append(metrics)
            
            # Feed metrics to anomaly detector if available (outside lock for performance)
            if self.anomaly_detector:
                # Use asyncio.create_task to avoid blocking
                asyncio.create_task(self._feed_metrics_to_detector_async(metrics))
            
            return metrics
    
    async def _feed_metrics_to_detector_async(self, metrics: SystemMetrics):
        """Feed metrics to detector asynchronously."""
        self._feed_metrics_to_detector(metrics)
    
    def _feed_metrics_to_detector(self, metrics: SystemMetrics):
        """Feed current metrics to anomaly detector for baseline establishment."""
        if not self.anomaly_detector:
            return
        
        # Record key metrics for anomaly detection
        # Response time
        self.anomaly_detector.record_metric(
            "avg_response_time_1min",
            metrics.avg_response_time_1min,
            {"timestamp": metrics.timestamp}
        )
        
        # Error rate
        error_metadata = {"timestamp": metrics.timestamp}
        if metrics.error_rate_1min > 0 and self.recent_errors:
            # Grab the most recent error context
            try:
                last_err = self.recent_errors[-1]
                msg = last_err.get("error_message", str(last_err))
                # Truncate if too long to avoid huge metadata
                error_metadata["latest_error"] = msg[:200]
            except:
                pass

        self.anomaly_detector.record_metric(
            "error_rate_1min",
            metrics.error_rate_1min,
            error_metadata
        )
        
        # Active requests
        self.anomaly_detector.record_metric(
            "active_requests",
            float(metrics.active_requests),
            {"timestamp": metrics.timestamp}
        )
        
        # Efficiency metrics
        if metrics.efficiency:
            self.anomaly_detector.record_metric(
                "requests_per_second",
                metrics.efficiency.requests_per_second,
                {"timestamp": metrics.timestamp}
            )
            self.anomaly_detector.record_metric(
                "cache_hit_rate",
                metrics.efficiency.cache_hit_rate,
                {"timestamp": metrics.timestamp}
            )
            self.anomaly_detector.record_metric(
                "semaphore_wait_time_avg_ms",
                metrics.efficiency.semaphore_wait_time_avg_ms,
                {"timestamp": metrics.timestamp}
            )
        
        # Resource usage
        if metrics.resource_usage:
            if "cpu_percent" in metrics.resource_usage:
                self.anomaly_detector.record_metric(
                    "cpu_percent",
                    metrics.resource_usage["cpu_percent"],
                    {"timestamp": metrics.timestamp}
                )
            if "memory_mb" in metrics.resource_usage:
                self.anomaly_detector.record_metric(
                    "memory_mb",
                    metrics.resource_usage["memory_mb"],
                    {"timestamp": metrics.timestamp}
                )
    
    def _calculate_efficiency_metrics(self, completed_count: int, total_tokens: int) -> EfficiencyMetrics:
        """Calculate efficiency metrics from tracked data."""
        # Throughput
        requests_per_second = completed_count / 60.0 if completed_count > 0 else 0.0
        tokens_per_second = total_tokens / 60.0 if total_tokens > 0 else 0.0
        
        # Cache efficiency
        total_cache_ops = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache_ops * 100) if total_cache_ops > 0 else 0.0
        
        # Connection pool utilization
        total_connections = self.connection_creates + self.connection_reuses
        connection_reuse_rate = (self.connection_reuses / total_connections * 100) if total_connections > 0 else 0.0
        
        # Semaphore wait times
        if self.semaphore_wait_times:
            wait_times = list(self.semaphore_wait_times)
            avg_wait_time = sum(wait_times) / len(wait_times)
        else:
            avg_wait_time = 0.0
        
        # Time breakdown by stage
        time_breakdown = {}
        for stage, durations in self.stage_durations.items():
            if durations:
                time_breakdown[stage] = sum(durations) / len(durations)
        
        # Network metrics
        network_bytes_sent = self.network_bytes_sent
        network_bytes_received = self.network_bytes_received
        
        # Average request/response sizes
        avg_request_size = sum(self.request_sizes) / len(self.request_sizes) if self.request_sizes else 0
        avg_response_size = sum(self.response_sizes) / len(self.response_sizes) if self.response_sizes else 0
        
        return EfficiencyMetrics(
            requests_per_second=requests_per_second,
            tokens_per_second=tokens_per_second,
            cache_hit_rate=cache_hit_rate,
            connection_pool_utilization=connection_reuse_rate,
            semaphore_wait_time_avg_ms=avg_wait_time,
            queue_depth=len(self.active_requests),  # Active requests as queue depth
            time_breakdown=time_breakdown,
            network_bytes_sent=network_bytes_sent,
            network_bytes_received=network_bytes_received,
            avg_request_size_bytes=int(avg_request_size),
            avg_response_size_bytes=int(avg_response_size),
        )
    
    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage (CPU, memory, etc.)."""
        try:
            import psutil
            process = psutil.Process()
            return {
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "open_files": len(process.open_files()),
                "threads": process.num_threads(),
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def _increment_counter(self, counter_name: str):
        """Increment a counter for the current minute."""
        now = time.time()
        minute = int(now // 60)
        self.request_counters[counter_name].append((minute, now))
    
    def record_semaphore_wait(self, wait_time_ms: float):
        """Record semaphore wait time (for efficiency analysis)."""
        async def _record():
            async with self._lock:
                self.semaphore_wait_times.append(wait_time_ms)
        # Fire and forget - don't block
        asyncio.create_task(_record())
    
    def record_request_size(self, size_bytes: int):
        """Record request body size."""
        async def _record():
            async with self._lock:
                self.request_sizes.append(size_bytes)
        asyncio.create_task(_record())
    
    def record_response_size(self, size_bytes: int):
        """Record response size."""
        async def _record():
            async with self._lock:
                self.response_sizes.append(size_bytes)
        asyncio.create_task(_record())
    
    def record_cache_hit(self):
        """Record a cache hit."""
        async def _record():
            async with self._lock:
                self.cache_hits += 1
        asyncio.create_task(_record())
    
    def record_cache_miss(self):
        """Record a cache miss."""
        async def _record():
            async with self._lock:
                self.cache_misses += 1
        asyncio.create_task(_record())
    
    def record_connection_reuse(self):
        """Record connection pool reuse."""
        async def _record():
            async with self._lock:
                self.connection_reuses += 1
        asyncio.create_task(_record())

    async def reset_history(self, targets: Optional[List[str]] = None):
        """
        Reset observability history based on targets.
        Targets: ['traces', 'counters', 'errors', 'health', 'efficiency', 'all']
        """
        if not targets or 'all' in targets:
            targets = ['traces', 'counters', 'errors', 'health', 'efficiency']
        
        async with self._lock:
            if 'traces' in targets:
                self.completed_requests.clear()
                self.performance_metrics.clear()
            
            if 'counters' in targets:
                self.request_counters.clear()
            
            if 'errors' in targets:
                self.recent_errors.clear()
                
            if 'health' in targets:
                self.component_health.clear()
                
            if 'efficiency' in targets:
                self.semaphore_wait_times.clear()
                self.stage_durations.clear()
                self.request_sizes.clear()
                self.response_sizes.clear()
                self.network_bytes_sent = 0
                self.network_bytes_received = 0
                self.cache_hits = 0
                self.cache_misses = 0
                self.connection_creates = 0
                self.connection_reuses = 0
                
        logger.info(f"Observability history reset for targets: {targets}")
        return {"ok": True, "reset": targets}

    
    def record_connection_create(self):
        """Record new connection creation."""
        async def _record():
            async with self._lock:
                self.connection_creates += 1
        asyncio.create_task(_record())
    
    def record_network_bytes(self, sent: int = 0, received: int = 0):
        """Record network bytes sent/received."""
        async def _record():
            async with self._lock:
                self.network_bytes_sent += sent
                self.network_bytes_received += received
        asyncio.create_task(_record())
    
    def export_data(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Export all observability data for analysis."""
        if output_path is None:
            output_path = self.storage_path / f"export_{int(time.time())}.json"
        
        data = {
            "export_timestamp": time.time(),
            "export_datetime": datetime.now().isoformat(),
            "active_requests": {
                req_id: asdict(req) for req_id, req in self.active_requests.items()
            },
            "recent_completed_requests": [
                asdict(req) for req in list(self.completed_requests)[-1000:]  # Last 1000
            ],
            "recent_performance_metrics": [
                asdict(m) for m in list(self.performance_metrics)[-5000:]  # Last 5000
            ],
            "component_health": {
                key: asdict(health) for key, health in self.component_health.items()
            },
            "recent_errors": list(self.recent_errors),
            "system_metrics_history": [
                asdict(m) for m in list(self.system_metrics_history)[-100:]  # Last 100
            ],
        }
        
        # Convert dataclasses to dicts recursively
        def convert(obj):
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert(item) for item in obj]
            elif hasattr(obj, '__dict__'):
                return convert(obj.__dict__)
            else:
                return obj
        
        data = convert(data)
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Exported observability data to {output_path}")
        return data
    
    async def get_stuck_requests(self, timeout_seconds: float = 30.0) -> List[Dict[str, Any]]:
        """Identify requests that appear to be stuck."""
        now = time.time()
        stuck = []
        
        async with self._lock:
            for req_id, lifecycle in self.active_requests.items():
                age = now - lifecycle.started_at
                if age > timeout_seconds:
                    # Calculate time since last stage change
                    if lifecycle.stages:
                        last_stage_time = max(lifecycle.stages.values())
                        time_since_last_stage = now - last_stage_time
                    else:
                        time_since_last_stage = age
                    
                    stuck.append({
                        "request_id": req_id,
                        "age_seconds": age,
                        "time_since_last_stage_seconds": time_since_last_stage,
                        "current_stage": lifecycle.stage.value,
                        "path": lifecycle.path,
                        "method": lifecycle.method,
                        "stages": lifecycle.stages,
                        "metadata": lifecycle.metadata,
                    })
        
        # Sort outside lock
        return sorted(stuck, key=lambda x: x["age_seconds"], reverse=True)
    
    async def get_performance_summary(self, component: Optional[str] = None, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance summary for analysis."""
        async with self._lock:
            # Filter in single pass instead of multiple iterations
            durations = []
            for m in self.performance_metrics:
                if component and m.component != component:
                    continue
                if operation and m.operation != operation:
                    continue
                durations.append(m.duration_ms)
        
        if not durations:
            return {"error": "No metrics found"}
        
        # Calculate statistics efficiently
        sorted_durations = sorted(durations)  # Only sort once
        count = len(sorted_durations)
        
        return {
            "count": count,
            "min_ms": sorted_durations[0],
            "max_ms": sorted_durations[-1],
            "avg_ms": sum(sorted_durations) / count,
            "p50_ms": sorted_durations[count // 2],
            "p95_ms": sorted_durations[int(count * 0.95)] if count > 0 else 0,
            "p99_ms": sorted_durations[int(count * 0.99)] if count > 0 else 0,
        }
    
    async def detect_anomalies(self) -> List[Any]:
        """Run anomaly detection on current metrics."""
        if not self.anomaly_detector:
            return []
            
        metrics = await self.get_system_metrics()
        anomalies = []
        
        # Check core metrics for anomalies
        check_metrics = [
            ("avg_response_time_1min", metrics.avg_response_time_1min),
            ("error_rate_1min", metrics.error_rate_1min),
            ("active_requests", float(metrics.active_requests))
        ]
        
        if metrics.efficiency:
            check_metrics.extend([
                ("requests_per_second", metrics.efficiency.requests_per_second),
                ("semaphore_wait_time_avg_ms", metrics.efficiency.semaphore_wait_time_avg_ms)
            ])
            
        for name, value in check_metrics:
            anomaly = self.anomaly_detector.check_anomaly(name, value)
            if anomaly:
                anomalies.append(anomaly)
                
        return anomalies

    async def get_anomalies(self, limit: int = 100) -> Dict[str, Any]:
        """Get recent detected anomalies."""
        if not self.anomaly_detector:
            return {"anomalies": [], "detector_enabled": False}
        
        anomalies = self.anomaly_detector.get_recent_anomalies(limit)
        return {
            "anomalies": [
                {
                    "id": a.id,
                    "status": a.status.value,
                    "metric_name": a.metric_name,
                    "current_value": a.current_value,
                    "baseline_value": a.baseline_value,
                    "deviation": a.deviation,
                    "severity": a.severity.value,
                    "timestamp": a.timestamp,
                    "metadata": a.metadata,
                    "message": f"Anomaly detected in {a.metric_name}: Current {a.current_value:.2f} (Baseline {a.baseline_value:.2f}, Deviation {a.deviation:.1f}σ)",
                }
                for a in anomalies
            ],
            "count": len(anomalies),
            "detector_enabled": True,
        }
    
    def get_anomaly_baselines(self) -> Dict[str, Any]:
        """Get current anomaly detection baselines."""
        if not self.anomaly_detector:
            return {"baselines": {}, "detector_enabled": False}
        
        baselines = self.anomaly_detector.get_baselines()
        return {
            "baselines": baselines,
            "detector_enabled": True,
            "sensitivity": self.anomaly_detector.sensitivity,
        }
    
    def clear_anomalies(self):
        """Clear all stored anomalies."""
        if self.anomaly_detector:
            self.anomaly_detector.clear_history()

    def acknowledge_anomaly(self, anomaly_id: str) -> bool:
        """Acknowledge an anomaly."""
        if self.anomaly_detector:
            return self.anomaly_detector.acknowledge_anomaly(anomaly_id)
        return False


# Global observability instance
_observability: Optional[ObservabilitySystem] = None


def get_observability() -> ObservabilitySystem:
    """Get or create the global observability instance."""
    global _observability
    if _observability is None:
        _observability = ObservabilitySystem()
    return _observability


@asynccontextmanager
async def track_request(request_id: str, method: str, path: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager for tracking a request lifecycle."""
    obs = get_observability()
    lifecycle = await obs.start_request(request_id, method, path, metadata)
    try:
        yield lifecycle
    finally:
        await obs.complete_request(request_id)

