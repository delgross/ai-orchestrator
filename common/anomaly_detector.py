"""
Anomaly Detection System

Detects abnormal patterns in system behavior using statistical analysis.
Supports both Gaussian (Z-Score) and Non-Parametric (IQR) detection.
"""

from __future__ import annotations

import logging
import statistics
import time
import math
import json
import os
import uuid
from collections import deque
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("anomaly_detector")


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AnomalyStatus(Enum):
    """Status tracking for anomalies."""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    IGNORED = "ignored"


@dataclass
class Anomaly:
    """Detected anomaly."""
    metric_name: str
    current_value: float
    baseline_value: float  # Mean or Median
    deviation: float       # Z-Score or IQR Multiplier
    severity: AnomalySeverity
    timestamp: float
    metadata: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: AnomalyStatus = AnomalyStatus.NEW

    def to_dict(self):
        """Convert to dictionary for serialization."""
        d = asdict(self)
        d['severity'] = self.severity.value
        d['status'] = self.status.value
        return d

    @classmethod
    def from_dict(cls, d):
        """Load from dictionary."""
        d['severity'] = AnomalySeverity(d['severity'])
        d['status'] = AnomalyStatus(d['status'])
        return cls(**d)


class AnomalyDetector:
    """Detects anomalies in system metrics using advanced statistical baselines."""
    
    def __init__(self, window_size: int = 1000, sensitivity: float = 2.0):
        """
        Initialize anomaly detector.
        
        Args:
            window_size: Number of recent values to use for baseline
            sensitivity: multiplier for threshold (StdDev for Gaussian, IQR for Non-Parametric)
        """
        self.window_size = window_size
        self.sensitivity = sensitivity
        
        # Metric history: metric_name -> deque of values
        self.metric_history: Dict[str, deque] = {}
        
        # Baselines: metric_name -> Dict of stats
        self.baselines: Dict[str, Dict[str, float]] = {}
        
        # Detected anomalies
        self.recent_anomalies: deque = deque(maxlen=1000)
        self.persistence_path = "data/anomalies.json"
        self._load_state()

    def _save_state(self):
        """Persist anomalies to disk."""
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            data = [a.to_dict() for a in self.recent_anomalies]
            with open(self.persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save anomalies: {e}")

    def _load_state(self):
        """Load anomalies from disk."""
        if not os.path.exists(self.persistence_path):
            return
        try:
            with open(self.persistence_path, 'r') as f:
                data = json.load(f)
                self.recent_anomalies = deque([Anomaly.from_dict(d) for d in data], maxlen=1000)
        except Exception as e:
            logger.error(f"Failed to load anomalies: {e}")

    def acknowledge_anomaly(self, anomaly_id: str) -> bool:
        """Mark an anomaly as acknowledged."""
        for a in self.recent_anomalies:
            if a.id == anomaly_id:
                a.status = AnomalyStatus.ACKNOWLEDGED
                self._save_state()
                return True
        return False
    
    # Metrics that typically follow a Log-Normal distribution (e.g., latency)
    LOG_NORMAL_METRICS = {"process_request", "total_response_time_ms", "avg_latency_ms"}
    
    def record_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Record a metric value and update baseline."""
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = deque(maxlen=self.window_size)
        
        self.metric_history[metric_name].append(value)
        
        # Update baseline periodically (every 50 values or when window is full)
        if len(self.metric_history[metric_name]) % 50 == 0:
            self._update_baseline(metric_name)
    
    def _update_baseline(self, metric_name: str):
        """Update statistical baseline for a metric using multiple methods."""
        values = list(self.metric_history[metric_name])
        if len(values) < 20:  # Need minimum data points for robust statistics
            return
        
        stats = {}
        
        # 1. Standard Gaussian Stats
        stats["mean"] = statistics.mean(values)
        try:
            stats["std_dev"] = statistics.stdev(values) if len(values) > 1 else 0.0
        except statistics.StatisticsError:
            stats["std_dev"] = 0.0
            
        # 2. Log-Normal Stats (for skewed data like latency)
        if metric_name in self.LOG_NORMAL_METRICS:
            # Shift by 1 to handle zero values
            log_values = [math.log(max(0.001, v)) for v in values]
            stats["log_mean"] = statistics.mean(log_values)
            stats["log_std_dev"] = statistics.stdev(log_values)
            
        # 3. Non-Parametric Stats (IQR) - Robust against outliers in history
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        q1 = sorted_vals[int(n * 0.25)]
        median = sorted_vals[int(n * 0.50)]
        q3 = sorted_vals[int(n * 0.75)]
        iqr = q3 - q1
        
        stats["median"] = median
        stats["iqr"] = iqr
        stats["q1"] = q1
        stats["q3"] = q3
        
        self.baselines[metric_name] = stats
    
    # Minimum absolute values required to trigger an anomaly
    METRIC_MIN_THRESHOLDS = {
        "requests_per_second": 5.0,      
        "error_rate_1min": 0.05,         
        "active_requests": 10.0,         
        "cpu_percent": 10.0,             
        "memory_mb": 100.0,              
    }

    def check_anomaly(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None) -> Optional[Anomaly]:
        """
        Check if a value is anomalous using the most appropriate statistical method.
        """
        if metric_name not in self.baselines:
            return None
        
        # Check minimum absolute threshold first
        if metric_name in self.METRIC_MIN_THRESHOLDS:
            if value < self.METRIC_MIN_THRESHOLDS[metric_name]:
                return None
        
        stats = self.baselines[metric_name]
        severity = None
        deviation = 0.0
        baseline_val = stats.get("median", stats.get("mean", 0.0))

        # Method A: Log-Normal Z-Score (Best for Latency)
        if metric_name in self.LOG_NORMAL_METRICS and "log_mean" in stats:
            log_val = math.log(max(0.001, value))
            log_mean = stats["log_mean"]
            log_std = stats["log_std_dev"]
            
            if log_std > 0:
                deviation = abs(log_val - log_mean) / log_std
                # For log-normal, we use tighter thresholds on the log scale
                if deviation >= self.sensitivity * 3:
                    severity = AnomalySeverity.CRITICAL
                elif deviation >= self.sensitivity * 2:
                    severity = AnomalySeverity.WARNING
                elif deviation >= self.sensitivity:
                    severity = AnomalySeverity.INFO
            
        # Method B: IQR (Best for Robustness against history outliers)
        # We use this as a secondary check or fallback
        elif "iqr" in stats and stats["iqr"] > 0:
            iqr = stats["iqr"]
            q3 = stats["q3"]
            q1 = stats["q1"]
            median = stats["median"]
            
            # Distance from the nearest quartile
            if value > q3:
                dist = (value - q3) / iqr
                baseline_val = q3
            elif value < q1:
                dist = (q1 - value) / iqr
                baseline_val = q1
            else:
                dist = 0
            
            # Map IQR distance to severity (typically 1.5x IQR is "outlier", 3x is "extreme")
            if dist >= 3.0:
                severity = AnomalySeverity.CRITICAL
                deviation = dist
            elif dist >= 1.5:
                # Only elevate to warning if Gaussian also agrees or for specific metrics
                severity = AnomalySeverity.WARNING
                deviation = dist
            elif dist >= 0.75:
                 severity = AnomalySeverity.INFO
                 deviation = dist

        # Method C: Standard Gaussian (Fallback)
        if severity is None and stats.get("std_dev", 0) > 0:
            mean = stats["mean"]
            std = stats["std_dev"]
            deviation = abs(value - mean) / std
            
            if deviation >= self.sensitivity * 3:
                severity = AnomalySeverity.CRITICAL
            elif deviation >= self.sensitivity * 2:
                severity = AnomalySeverity.WARNING
            elif deviation >= self.sensitivity:
                severity = AnomalySeverity.INFO
        
        if severity:
            anomaly = Anomaly(
                metric_name=metric_name,
                current_value=value,
                baseline_value=baseline_val,
                deviation=deviation,
                severity=severity,
                timestamp=time.time(),
                metadata=metadata or {}
            )
            self.recent_anomalies.append(anomaly)
            self._save_state()
            return anomaly
            
        return None
    
    def get_recent_anomalies(self, limit: int = 100) -> List[Anomaly]:
        """Get recent anomalies."""
        return list(self.recent_anomalies)[-limit:]
    
    def get_baselines(self) -> Dict[str, Dict[str, Any]]:
        """Get current baselines for all metrics."""
        return {
            name: {
                **stats,
                "samples": len(self.metric_history.get(name, []))
            }
            for name, stats in self.baselines.items()
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






