"""
Quality Metrics Tracker for Tool Result Processing

Tracks the effectiveness of quality mitigation strategies and enables
A/B testing of different truncation approaches to continuously improve
answer quality.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json

logger = logging.getLogger("agent_runner.quality_metrics")


@dataclass
class QualityEvent:
    """Represents a quality processing event"""
    timestamp: float
    tool_name: str
    strategy: str
    original_length: int
    processed_length: int
    quality_tier: str
    was_truncated: bool
    adaptive_improved: bool = False
    ai_generated: bool = False
    user_feedback: Optional[int] = None  # 1-5 quality rating
    processing_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "tool_name": self.tool_name,
            "strategy": self.strategy,
            "original_length": self.original_length,
            "processed_length": self.processed_length,
            "quality_tier": self.quality_tier,
            "was_truncated": self.was_truncated,
            "adaptive_improved": self.adaptive_improved,
            "ai_generated": self.ai_generated,
            "user_feedback": self.user_feedback,
            "processing_time": self.processing_time
        }


@dataclass
class ABTestVariant:
    """Represents an A/B test variant"""
    name: str
    strategy: str
    parameters: Dict[str, Any]
    active: bool = True
    sample_size: int = 100  # Minimum samples before evaluation
    events: List[QualityEvent] = field(default_factory=list)

    def add_event(self, event: QualityEvent):
        """Add an event to this variant"""
        self.events.append(event)

    def get_metrics(self) -> Dict[str, Any]:
        """Calculate metrics for this variant"""
        if not self.events:
            return {"sample_size": 0}

        total_events = len(self.events)
        truncated_events = sum(1 for e in self.events if e.was_truncated)
        ai_generated = sum(1 for e in self.events if e.ai_generated)
        adaptive_improved = sum(1 for e in self.events if e.adaptive_improved)

        # Quality scores (if available)
        quality_scores = [e.user_feedback for e in self.events if e.user_feedback is not None]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None

        # Length preservation ratio
        avg_length_ratio = sum(e.processed_length / e.original_length for e in self.events) / total_events

        return {
            "sample_size": total_events,
            "truncation_rate": truncated_events / total_events,
            "ai_generation_rate": ai_generated / total_events,
            "adaptive_improvement_rate": adaptive_improved / total_events,
            "average_length_ratio": avg_length_ratio,
            "average_quality_score": avg_quality,
            "quality_score_count": len(quality_scores)
        }


class QualityMetricsTracker:
    """
    Tracks quality metrics for tool result processing and enables
    A/B testing of different truncation strategies.
    """

    def __init__(self):
        self.events: List[QualityEvent] = []
        self.max_events = 10000  # Rolling window of events

        # A/B testing
        self.ab_tests: Dict[str, List[ABTestVariant]] = {}
        self.active_tests: Dict[str, ABTestVariant] = {}

        # Aggregated metrics
        self.metrics = {
            "total_events": 0,
            "strategy_performance": defaultdict(lambda: {"count": 0, "quality_sum": 0, "quality_count": 0}),
            "tool_performance": defaultdict(lambda: {"count": 0, "avg_length_ratio": 0}),
            "daily_quality_trends": defaultdict(list)
        }

    def record_quality_event(self, tool_name: str, processing_metadata: Dict[str, Any],
                           original_length: int, processed_length: int, quality_tier: str,
                           processing_time: float = 0.0):
        """Record a quality processing event"""

        event = QualityEvent(
            timestamp=time.time(),
            tool_name=tool_name,
            strategy=processing_metadata.get("strategy", "unknown"),
            original_length=original_length,
            processed_length=processed_length,
            quality_tier=quality_tier,
            was_truncated=processing_metadata.get("truncated", False),
            adaptive_improved=processing_metadata.get("adaptive_improved", False),
            ai_generated=processing_metadata.get("ai_generated", False),
            processing_time=processing_time
        )

        self.events.append(event)

        # Maintain rolling window
        if len(self.events) > self.max_events:
            self.events.pop(0)

        # Update aggregated metrics
        self._update_aggregated_metrics(event)

        # Add to active A/B tests
        for test_name, variant in self.active_tests.items():
            variant.add_event(event)

        self.metrics["total_events"] += 1

        logger.debug(f"Recorded quality event: {tool_name} - {event.strategy} - truncated: {event.was_truncated}")

    def record_user_feedback(self, event_index: int, quality_score: int):
        """Record user feedback on a specific event"""
        if 0 <= event_index < len(self.events):
            self.events[event_index].user_feedback = quality_score
            # Update aggregated metrics
            strategy = self.events[event_index].strategy
            self.metrics["strategy_performance"][strategy]["quality_sum"] += quality_score
            self.metrics["strategy_performance"][strategy]["quality_count"] += 1

            logger.info(f"User feedback recorded: event {event_index}, score {quality_score}")

    def start_ab_test(self, test_name: str, variants: List[Dict[str, Any]]):
        """Start an A/B test with multiple variants"""
        if test_name in self.ab_tests:
            logger.warning(f"A/B test {test_name} already exists")
            return

        test_variants = []
        for variant_config in variants:
            variant = ABTestVariant(
                name=variant_config["name"],
                strategy=variant_config["strategy"],
                parameters=variant_config.get("parameters", {}),
                sample_size=variant_config.get("sample_size", 100)
            )
            test_variants.append(variant)

        self.ab_tests[test_name] = test_variants

        # Activate the first variant by default
        if test_variants:
            self.active_tests[test_name] = test_variants[0]

        logger.info(f"Started A/B test: {test_name} with {len(test_variants)} variants")

    def get_ab_test_results(self, test_name: str) -> Optional[Dict[str, Any]]:
        """Get results for an A/B test"""
        if test_name not in self.ab_tests:
            return None

        variants = self.ab_tests[test_name]
        results = {}

        for variant in variants:
            metrics = variant.get_metrics()
            results[variant.name] = {
                "strategy": variant.strategy,
                "parameters": variant.parameters,
                "metrics": metrics,
                "is_active": self.active_tests.get(test_name) == variant
            }

        # Determine winner if all variants have sufficient samples
        winners = []
        for variant in variants:
            if variant.get_metrics()["sample_size"] >= variant.sample_size:
                winners.append(variant)

        if winners:
            # Simple winner selection based on quality score
            best_variant = max(winners,
                             key=lambda v: v.get_metrics().get("average_quality_score", 0))
            results["winner"] = best_variant.name

        return results

    def get_quality_report(self) -> Dict[str, Any]:
        """Generate a comprehensive quality report"""
        report = {
            "summary": {
                "total_events": self.metrics["total_events"],
                "time_window": f"{len(self.events)} events ({self.max_events} max)",
                "active_ab_tests": len(self.active_tests)
            },
            "strategy_performance": {},
            "tool_performance": {},
            "trends": {}
        }

        # Strategy performance
        for strategy, data in self.metrics["strategy_performance"].items():
            quality_avg = data["quality_sum"] / data["quality_count"] if data["quality_count"] > 0 else None
            report["strategy_performance"][strategy] = {
                "total_uses": data["count"],
                "average_quality": quality_avg,
                "quality_feedback_count": data["quality_count"]
            }

        # Tool performance
        for tool, data in self.metrics["tool_performance"].items():
            report["tool_performance"][tool] = {
                "total_uses": data["count"],
                "average_length_ratio": data["avg_length_ratio"]
            }

        # Recent trends (last 100 events)
        recent_events = self.events[-100:] if len(self.events) >= 100 else self.events
        if recent_events:
            truncated_rate = sum(1 for e in recent_events if e.was_truncated) / len(recent_events)
            ai_rate = sum(1 for e in recent_events if e.ai_generated) / len(recent_events)
            avg_quality = sum(e.user_feedback for e in recent_events if e.user_feedback) / sum(1 for e in recent_events if e.user_feedback) if any(e.user_feedback for e in recent_events) else None

            report["trends"]["recent_100"] = {
                "truncation_rate": truncated_rate,
                "ai_generation_rate": ai_rate,
                "average_quality": avg_quality
            }

        return report

    def _update_aggregated_metrics(self, event: QualityEvent):
        """Update aggregated metrics with new event"""
        # Strategy performance
        strategy_data = self.metrics["strategy_performance"][event.strategy]
        strategy_data["count"] += 1
        if event.user_feedback is not None:
            strategy_data["quality_sum"] += event.user_feedback
            strategy_data["quality_count"] += 1

        # Tool performance
        tool_data = self.metrics["tool_performance"][event.tool_name]
        tool_data["count"] += 1
        length_ratio = event.processed_length / event.original_length if event.original_length > 0 else 1.0
        # Rolling average
        tool_data["avg_length_ratio"] = (tool_data["avg_length_ratio"] * (tool_data["count"] - 1) + length_ratio) / tool_data["count"]

        # Daily trends
        day_key = time.strftime("%Y-%m-%d", time.localtime(event.timestamp))
        self.metrics["daily_quality_trends"][day_key].append(event)

    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for backup/analysis"""
        return {
            "events": [event.to_dict() for event in self.events],
            "ab_tests": {name: [v.__dict__ for v in variants] for name, variants in self.ab_tests.items()},
            "active_tests": list(self.active_tests.keys()),
            "aggregated_metrics": dict(self.metrics)
        }

    def import_metrics(self, data: Dict[str, Any]):
        """Import metrics from backup"""
        # Reconstruct events
        self.events = [QualityEvent(**event_data) for event_data in data.get("events", [])]

        # Reconstruct A/B tests
        for test_name, variants_data in data.get("ab_tests", {}).items():
            variants = [ABTestVariant(**v) for v in variants_data]
            self.ab_tests[test_name] = variants

        # Restore active tests
        for test_name in data.get("active_tests", []):
            if test_name in self.ab_tests and self.ab_tests[test_name]:
                self.active_tests[test_name] = self.ab_tests[test_name][0]

        # Restore aggregated metrics
        self.metrics.update(data.get("aggregated_metrics", {}))

        logger.info(f"Imported metrics: {len(self.events)} events, {len(self.ab_tests)} A/B tests")

    def reset_metrics(self):
        """Reset all metrics (for testing)"""
        self.events.clear()
        self.ab_tests.clear()
        self.active_tests.clear()
        self.metrics = {
            "total_events": 0,
            "strategy_performance": defaultdict(lambda: {"count": 0, "quality_sum": 0, "quality_count": 0}),
            "tool_performance": defaultdict(lambda: {"count": 0, "avg_length_ratio": 0}),
            "daily_quality_trends": defaultdict(list)
        }
        logger.info("Quality metrics reset")