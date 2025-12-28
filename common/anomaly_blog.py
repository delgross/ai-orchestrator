"""
Anomaly Blog Integration

Automatically writes blog entries when anomalies are detected.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from common.system_blog import (
    BlogCategory,
    BlogEntry,
    BlogSeverity,
    get_blog,
)
from common.observability import SystemMetrics

logger = logging.getLogger("anomaly_blog")


def create_anomaly_blog_entry(
    anomaly: Any,
    metrics: SystemMetrics,
    context: Optional[Dict[str, Any]] = None,
) -> BlogEntry:
    """
    Create a blog entry for a detected anomaly.
    
    Args:
        anomaly: Anomaly object from anomaly detector
        metrics: Current system metrics
        context: Additional context (optional)
    
    Returns:
        BlogEntry ready to be written
    """
    # Map anomaly severity to blog severity
    severity_map = {
        "critical": BlogSeverity.CRITICAL,
        "warning": BlogSeverity.WARNING,
        "info": BlogSeverity.INFO,
    }
    
    blog_severity = severity_map.get(anomaly.severity.value, BlogSeverity.WARNING)
    
    # Calculate percentage change
    if anomaly.baseline_value != 0:
        pct_change = ((anomaly.current_value - anomaly.baseline_value) / anomaly.baseline_value) * 100
    else:
        pct_change = 0.0
    
    # Build human-readable content
    content_lines = [
        f"An anomaly was detected in the **{anomaly.metric_name}** metric.",
        "",
        "## Details",
        "",
        f"- **Current Value**: {anomaly.current_value:.2f}",
        f"- **Baseline Value**: {anomaly.baseline_value:.2f}",
        f"- **Deviation**: {anomaly.deviation:.2f} standard deviations",
        f"- **Change**: {pct_change:+.1f}%",
        f"- **Severity**: {anomaly.severity.value.upper()}",
        "",
    ]
    
    # Add context about what this metric means
    metric_descriptions = {
        "avg_response_time_1min": "Average response time over the last minute. High values indicate slow system performance.",
        "error_rate_1min": "Error rate over the last minute. High values indicate system reliability issues.",
        "active_requests": "Number of currently active requests. High values may indicate system overload.",
        "requests_per_second": "Request throughput. Low values may indicate system degradation.",
        "cache_hit_rate": "Cache efficiency. Low values may indicate cache configuration issues.",
        "semaphore_wait_time_avg_ms": "Average time requests wait for concurrency slots. High values indicate resource contention.",
        "cpu_percent": "CPU usage percentage. High values indicate CPU-bound operations.",
        "memory_mb": "Memory usage in megabytes. Increasing values may indicate memory leaks.",
    }
    
    description = metric_descriptions.get(anomaly.metric_name, "System metric indicating performance or health status.")
    content_lines.append(f"**What this means**: {description}")
    content_lines.append("")
    
    # Add system context
    content_lines.append("## System Context")
    content_lines.append("")
    content_lines.append(f"- **Active Requests**: {metrics.active_requests}")
    content_lines.append(f"- **Completed Requests (1min)**: {metrics.completed_requests_1min}")
    content_lines.append(f"- **Error Rate (1min)**: {metrics.error_rate_1min:.2%}")
    content_lines.append(f"- **Avg Response Time (1min)**: {metrics.avg_response_time_1min:.2f}ms")
    content_lines.append("")
    
    if metrics.efficiency:
        content_lines.append("### Efficiency Metrics")
        content_lines.append("")
        content_lines.append(f"- **Requests/sec**: {metrics.efficiency.requests_per_second:.2f}")
        content_lines.append(f"- **Cache Hit Rate**: {metrics.efficiency.cache_hit_rate:.1f}%")
        content_lines.append(f"- **Queue Depth**: {metrics.efficiency.queue_depth}")
        content_lines.append("")
    
    if metrics.resource_usage:
        content_lines.append("### Resource Usage")
        content_lines.append("")
        if "cpu_percent" in metrics.resource_usage:
            content_lines.append(f"- **CPU**: {metrics.resource_usage['cpu_percent']:.1f}%")
        if "memory_mb" in metrics.resource_usage:
            content_lines.append(f"- **Memory**: {metrics.resource_usage['memory_mb']:.1f} MB")
        content_lines.append("")
    
    # Generate suggested actions based on metric type
    suggested_actions = _generate_suggested_actions(anomaly, metrics)
    
    if suggested_actions:
        content_lines.append("## Suggested Actions")
        content_lines.append("")
        for i, action in enumerate(suggested_actions, 1):
            content_lines.append(f"{i}. {action}")
        content_lines.append("")
    
    content = "\n".join(content_lines)
    
    # Build structured data (machine-readable)
    structured_data = {
        "anomaly": {
            "metric_name": anomaly.metric_name,
            "current_value": anomaly.current_value,
            "baseline_value": anomaly.baseline_value,
            "deviation": anomaly.deviation,
            "severity": anomaly.severity.value,
            "percentage_change": pct_change,
        },
        "system_state": {
            "active_requests": metrics.active_requests,
            "completed_requests_1min": metrics.completed_requests_1min,
            "error_rate_1min": metrics.error_rate_1min,
            "avg_response_time_1min": metrics.avg_response_time_1min,
        },
        "metadata": anomaly.metadata,
    }
    
    if metrics.efficiency:
        structured_data["efficiency"] = {
            "requests_per_second": metrics.efficiency.requests_per_second,
            "cache_hit_rate": metrics.efficiency.cache_hit_rate,
            "queue_depth": metrics.efficiency.queue_depth,
        }
    
    if metrics.resource_usage:
        structured_data["resource_usage"] = metrics.resource_usage
    
    if context:
        structured_data["additional_context"] = context
    
    # Create blog entry
    entry = BlogEntry(
        timestamp=anomaly.timestamp,
        category=BlogCategory.ANOMALY,
        severity=blog_severity,
        title=f"Anomaly: {anomaly.metric_name}",
        source="anomaly_detector",
        tags=["anomaly", anomaly.metric_name, anomaly.severity.value],
        metadata={
            "anomaly_id": f"{anomaly.metric_name}_{anomaly.timestamp}",
            **anomaly.metadata,
        },
        content=content,
        structured_data=structured_data,
        suggested_actions=suggested_actions,
        resolution_status="open",
    )
    
    return entry


def _generate_suggested_actions(anomaly: Any, metrics: SystemMetrics) -> list[str]:
    """Generate suggested actions based on anomaly type and system state."""
    actions = []
    metric = anomaly.metric_name
    
    if metric == "avg_response_time_1min":
        if anomaly.current_value > anomaly.baseline_value * 2:
            actions.append("Check for slow upstream services or database queries")
            actions.append("Review recent code changes that might affect performance")
            if metrics.efficiency and metrics.efficiency.queue_depth > 10:
                actions.append("Consider increasing concurrency limits or scaling resources")
    
    elif metric == "error_rate_1min":
        if anomaly.current_value > 0.1:  # >10% error rate
            actions.append("Check error logs for patterns")
            actions.append("Review component health status")
            actions.append("Check for recent configuration changes")
    
    elif metric == "active_requests":
        if anomaly.current_value > 50:
            actions.append("Monitor system load and resource usage")
            actions.append("Check if requests are completing or getting stuck")
    
    elif metric == "cache_hit_rate":
        if anomaly.current_value < 50:  # <50% hit rate
            actions.append("Review cache configuration and TTL settings")
            actions.append("Consider increasing cache size if memory allows")
    
    elif metric == "semaphore_wait_time_avg_ms":
        if anomaly.current_value > 100:  # >100ms wait
            actions.append("Consider increasing concurrency limits")
            actions.append("Review if semaphore limits are too restrictive")
    
    elif metric == "cpu_percent":
        if anomaly.current_value > 80:
            actions.append("Check for CPU-intensive operations")
            actions.append("Consider optimizing hot code paths")
            actions.append("Review if system needs more CPU resources")
    
    elif metric == "memory_mb":
        if anomaly.current_value > anomaly.baseline_value * 1.5:
            actions.append("Check for memory leaks")
            actions.append("Review memory usage patterns")
            actions.append("Consider restarting service if memory continues to grow")
    
    # General actions
    if anomaly.severity.value == "critical":
        actions.append("Investigate immediately - critical system issue detected")
    
    return actions


def write_anomaly_to_blog(anomaly: Any, metrics: SystemMetrics, context: Optional[Dict[str, Any]] = None) -> Path:
    """
    Write an anomaly to the blog.
    
    Returns:
        Path to the written blog entry file
    """
    try:
        blog = get_blog()
        entry = create_anomaly_blog_entry(anomaly, metrics, context)
        file_path = blog.write_entry(entry)
        logger.info(f"Anomaly blog entry written: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to write anomaly to blog: {e}", exc_info=True)
        raise





