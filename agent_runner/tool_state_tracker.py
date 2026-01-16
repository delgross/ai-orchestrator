"""
Tool State Tracker for Conversation State Compression

Tracks tool execution patterns and provides intelligent recommendations
for tool selection and avoidance based on success/failure history.
"""

import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

logger = logging.getLogger("agent_runner.tool_state_tracker")


@dataclass
class ToolPerformanceMetrics:
    """Performance metrics for a specific tool"""
    tool_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    consecutive_failures: int = 0
    last_success_time: Optional[float] = None
    last_failure_time: Optional[float] = None
    average_execution_time: float = 0.0
    execution_times: List[float] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate for this tool"""
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls

    @property
    def is_recently_failing(self) -> bool:
        """Check if tool is experiencing recent failures"""
        if self.consecutive_failures >= 2:
            return True
        if self.last_failure_time and (time.time() - self.last_failure_time) < 300:  # 5 minutes
            return True
        return False

    def record_execution(self, success: bool, execution_time: Optional[float] = None):
        """Record a tool execution"""
        self.total_calls += 1

        if success:
            self.successful_calls += 1
            self.consecutive_failures = 0
            self.last_success_time = time.time()
        else:
            self.failed_calls += 1
            self.consecutive_failures += 1
            self.last_failure_time = time.time()

        if execution_time is not None:
            self.execution_times.append(execution_time)
            # Keep only last 10 execution times for moving average
            if len(self.execution_times) > 10:
                self.execution_times.pop(0)
            self.average_execution_time = sum(self.execution_times) / len(self.execution_times)

    def get_recommendation(self) -> Tuple[str, float]:
        """
        Get recommendation score for using this tool
        Returns: (recommendation_type, confidence_score)
        """
        if self.is_recently_failing:
            return "avoid", 0.8

        if self.success_rate > 0.8 and self.total_calls >= 3:
            return "prefer", 0.9

        if self.success_rate < 0.3 and self.total_calls >= 3:
            return "avoid", 0.7

        return "neutral", 0.5


class ToolStateTracker:
    """
    Tracks tool performance across conversations and provides
    intelligent tool selection recommendations.
    """

    def __init__(self):
        self.tool_metrics: Dict[str, ToolPerformanceMetrics] = {}
        self.global_stats = {
            "total_tool_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "most_reliable_tools": [],
            "most_problematic_tools": []
        }

    def record_tool_execution(self, tool_name: str, success: bool,
                             execution_time: Optional[float] = None):
        """Record a tool execution and update metrics"""
        if tool_name not in self.tool_metrics:
            self.tool_metrics[tool_name] = ToolPerformanceMetrics(tool_name=tool_name)

        self.tool_metrics[tool_name].record_execution(success, execution_time)

        # Update global stats
        self.global_stats["total_tool_calls"] += 1
        if success:
            self.global_stats["successful_calls"] += 1
        else:
            self.global_stats["failed_calls"] += 1

        # Update rankings
        self._update_rankings()

        logger.debug(f"Tool execution recorded: {tool_name} ({'success' if success else 'failure'})")

    def get_tool_recommendation(self, tool_name: str) -> Tuple[str, float, str]:
        """
        Get recommendation for using a specific tool

        Returns:
            (recommendation, confidence, reason)
        """
        if tool_name not in self.tool_metrics:
            return "unknown", 0.0, "No execution history"

        metrics = self.tool_metrics[tool_name]
        recommendation, confidence = metrics.get_recommendation()

        # Generate human-readable reason
        if recommendation == "avoid":
            if metrics.consecutive_failures >= 2:
                reason = f"Consecutive failures ({metrics.consecutive_failures})"
            elif metrics.success_rate < 0.3:
                reason = f"Low success rate ({metrics.success_rate:.1%})"
            else:
                reason = "Recent failures"
        elif recommendation == "prefer":
            reason = f"High reliability ({metrics.success_rate:.1%} over {metrics.total_calls} calls)"
        else:
            reason = f"Moderate performance ({metrics.success_rate:.1%})"

        return recommendation, confidence, reason

    def get_alternative_tools(self, failed_tool: str, available_tools: List[str]) -> List[Tuple[str, float]]:
        """
        Suggest alternative tools when a tool fails

        Returns:
            List of (tool_name, confidence_score) tuples, sorted by confidence
        """
        alternatives = []

        for tool_name in available_tools:
            if tool_name == failed_tool:
                continue

            recommendation, confidence, _ = self.get_tool_recommendation(tool_name)
            if recommendation in ["prefer", "neutral"]:
                alternatives.append((tool_name, confidence))

        # Sort by confidence (highest first)
        alternatives.sort(key=lambda x: x[1], reverse=True)
        return alternatives[:3]  # Top 3 alternatives

    def should_retry_tool(self, tool_name: str, current_failure_count: int = 1) -> Tuple[bool, str]:
        """
        Determine if a failed tool should be retried

        Returns:
            (should_retry, reason)
        """
        if tool_name not in self.tool_metrics:
            return True, "No failure history - can retry"

        metrics = self.tool_metrics[tool_name]

        # Don't retry if consecutive failures are high
        if metrics.consecutive_failures >= 3:
            return False, f"Too many consecutive failures ({metrics.consecutive_failures})"

        # Don't retry if overall success rate is very low
        if metrics.success_rate < 0.1 and metrics.total_calls >= 5:
            return False, f"Very low success rate ({metrics.success_rate:.1%})"

        # Allow retry with diminishing returns for repeated failures
        if current_failure_count <= 2:
            return True, "Recent failures but worth retrying"
        else:
            return False, f"Multiple failures in this session ({current_failure_count})"

    def get_tool_performance_summary(self) -> str:
        """Generate a summary of tool performance"""
        if not self.tool_metrics:
            return "No tool execution data available"

        total_tools = len(self.tool_metrics)
        reliable_tools = [name for name, metrics in self.tool_metrics.items()
                         if metrics.success_rate > 0.8 and metrics.total_calls >= 3]
        problematic_tools = [name for name, metrics in self.tool_metrics.items()
                           if metrics.is_recently_failing]

        summary_parts = [
            f"Tool Performance: {len(reliable_tools)}/{total_tools} tools reliable",
        ]

        if problematic_tools:
            summary_parts.append(f"⚠️ Problematic: {', '.join(problematic_tools[:3])}")

        if reliable_tools:
            summary_parts.append(f"✅ Reliable: {', '.join(reliable_tools[:3])}")

        return " | ".join(summary_parts)

    def get_detailed_tool_report(self, tool_name: str) -> Optional[str]:
        """Get detailed performance report for a specific tool"""
        if tool_name not in self.tool_metrics:
            return None

        metrics = self.tool_metrics[tool_name]
        report = f"""
Tool: {tool_name}
- Total calls: {metrics.total_calls}
- Success rate: {metrics.success_rate:.1%}
- Consecutive failures: {metrics.consecutive_failures}
- Average execution time: {metrics.average_execution_time:.2f}s
- Last success: {time.ctime(metrics.last_success_time) if metrics.last_success_time else 'Never'}
- Last failure: {time.ctime(metrics.last_failure_time) if metrics.last_failure_time else 'Never'}
"""

        recommendation, confidence, reason = self.get_tool_recommendation(tool_name)
        report += f"Recommendation: {recommendation.upper()} ({confidence:.1%} confidence)\n"
        report += f"Reason: {reason}"

        return report.strip()

    def _update_rankings(self):
        """Update global rankings of most reliable/problematic tools"""
        if not self.tool_metrics:
            return

        # Most reliable (highest success rate, minimum 3 calls)
        reliable = [(name, metrics.success_rate) for name, metrics in self.tool_metrics.items()
                   if metrics.total_calls >= 3]
        reliable.sort(key=lambda x: x[1], reverse=True)
        self.global_stats["most_reliable_tools"] = [name for name, _ in reliable[:5]]

        # Most problematic (recent failures)
        problematic = [(name, metrics.consecutive_failures) for name, metrics in self.tool_metrics.items()
                      if metrics.is_recently_failing]
        problematic.sort(key=lambda x: x[1], reverse=True)
        self.global_stats["most_problematic_tools"] = [name for name, _ in problematic[:5]]

    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for persistence/analysis"""
        return {
            "tool_metrics": {name: {
                "total_calls": metrics.total_calls,
                "successful_calls": metrics.successful_calls,
                "failed_calls": metrics.failed_calls,
                "consecutive_failures": metrics.consecutive_failures,
                "success_rate": metrics.success_rate,
                "average_execution_time": metrics.average_execution_time,
                "last_success_time": metrics.last_success_time,
                "last_failure_time": metrics.last_failure_time,
                "execution_times": metrics.execution_times
            } for name, metrics in self.tool_metrics.items()},
            "global_stats": self.global_stats
        }

    def import_metrics(self, data: Dict[str, Any]):
        """Import metrics from exported data"""
        for tool_name, metrics_data in data.get("tool_metrics", {}).items():
            metrics = ToolPerformanceMetrics(tool_name=tool_name)
            metrics.total_calls = metrics_data["total_calls"]
            metrics.successful_calls = metrics_data["successful_calls"]
            metrics.failed_calls = metrics_data["failed_calls"]
            metrics.consecutive_failures = metrics_data["consecutive_failures"]
            metrics.average_execution_time = metrics_data["average_execution_time"]
            metrics.last_success_time = metrics_data["last_success_time"]
            metrics.last_failure_time = metrics_data["last_failure_time"]
            metrics.execution_times = metrics_data["execution_times"]
            self.tool_metrics[tool_name] = metrics

        self.global_stats.update(data.get("global_stats", {}))
        self._update_rankings()

        logger.info(f"Imported metrics for {len(self.tool_metrics)} tools")