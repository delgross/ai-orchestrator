"""
Anomaly Detection System

Detects abnormal patterns in system behavior using statistical analysis.
"""

from __future__ import annotations

import logging
import statistics
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("anomaly_detector")


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Detected anomaly."""
    metric_name: str
    current_value: float
    baseline_value: float
    deviation: float
    severity: AnomalySeverity
    timestamp: float
    metadata: Dict[str, Any]


class AnomalyDetector:
    """Detects anomalies in system metrics using statistical baselines."""
    
    def __init__(self, window_size: int = 1000, sensitivity: float = 2.0):
        """
        Initialize anomaly detector.
        
        Args:
            window_size: Number of recent values to use for baseline
            sensitivity: Number of standard deviations for anomaly threshold (default: 2.0 = ~95% confidence)
        """
        self.window_size = window_size
        self.sensitivity = sensitivity
        
        # Metric history: metric_name -> deque of values
        self.metric_history: Dict[str, deque] = {}
        
        # Baselines: metric_name -> (mean, std_dev)
        self.baselines: Dict[str, tuple[float, float]] = {}
        
        # Detected anomalies
        self.recent_anomalies: deque = deque(maxlen=1000)
    
    def record_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Record a metric value and update baseline."""
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = deque(maxlen=self.window_size)
        
        self.metric_history[metric_name].append(value)
        
        # Update baseline periodically (every 100 values or when window is full)
        if len(self.metric_history[metric_name]) >= min(100, self.window_size):
            self._update_baseline(metric_name)
    
    def _update_baseline(self, metric_name: str):
        """Update statistical baseline for a metric."""
        values = list(self.metric_history[metric_name])
        if len(values) < 10:  # Need minimum data points
            return
        
        mean = statistics.mean(values)
        try:
            std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
        except statistics.StatisticsError:
            std_dev = 0.0
        
        self.baselines[metric_name] = (mean, std_dev)
    
    def check_anomaly(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None) -> Optional[Anomaly]:
        """
        Check if a value is anomalous.
        
        Returns:
            Anomaly object if detected, None otherwise
        """
        if metric_name not in self.baselines:
            # Not enough data yet
            return None
        
        mean, std_dev = self.baselines[metric_name]
        
        if std_dev == 0:
            # No variance - can't detect anomalies
            return None
        
        deviation = abs(value - mean) / std_dev if std_dev > 0 else 0
        
        # Determine severity
        if deviation >= self.sensitivity * 3:
            severity = AnomalySeverity.CRITICAL
        elif deviation >= self.sensitivity * 2:
            severity = AnomalySeverity.WARNING
        elif deviation >= self.sensitivity:
            severity = AnomalySeverity.INFO
        else:
            return None  # Not anomalous
        
        anomaly = Anomaly(
            metric_name=metric_name,
            current_value=value,
            baseline_value=mean,
            deviation=deviation,
            severity=severity,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        self.recent_anomalies.append(anomaly)
        return anomaly
    
    def get_recent_anomalies(self, limit: int = 100) -> List[Anomaly]:
        """Get recent anomalies."""
        return list(self.recent_anomalies)[-limit:]
    
    def get_baselines(self) -> Dict[str, Dict[str, float]]:
        """Get current baselines for all metrics."""
        return {
            name: {
                "mean": mean,
                "std_dev": std_dev,
                "samples": len(self.metric_history.get(name, []))
            }
            for name, (mean, std_dev) in self.baselines.items()
        }
    
    def clear_history(self):
        """Clear all detected anomalies."""
        self.recent_anomalies.clear()


# Global instance
_anomaly_detector: Optional[AnomalyDetector] = None


def get_anomaly_detector() -> AnomalyDetector:
    """Get or create global anomaly detector."""
    global _anomaly_detector
    if _anomaly_detector is None:
        _anomaly_detector = AnomalyDetector()
    return _anomaly_detector






