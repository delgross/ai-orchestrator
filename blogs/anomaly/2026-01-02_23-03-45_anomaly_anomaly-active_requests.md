---
timestamp: 1767413025.314612
datetime: '2026-01-02T23:03:45.314612'
category: anomaly
severity: critical
title: 'Anomaly: active_requests'
source: anomaly_detector
tags:
- anomaly
- active_requests
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: active_requests_1767413025.314612
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 12.0
    baseline_value: 2.0
    deviation: 5.0
    severity: critical
    percentage_change: 500.0
  system_state:
    active_requests: 12
    completed_requests_1min: 621
    error_rate_1min: 0.0
    avg_response_time_1min: 708.4543850878779
  metadata: {}
  efficiency:
    requests_per_second: 10.35
    cache_hit_rate: 0.0
    queue_depth: 12
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 12.00
- **Baseline Value**: 2.00
- **Deviation**: 5.00 standard deviations
- **Change**: +500.0%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 12
- **Completed Requests (1min)**: 621
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 708.45ms

### Efficiency Metrics

- **Requests/sec**: 10.35
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 12

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 12.0,
    "baseline_value": 2.0,
    "deviation": 5.0,
    "severity": "critical",
    "percentage_change": 500.0
  },
  "system_state": {
    "active_requests": 12,
    "completed_requests_1min": 621,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 708.4543850878779
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.35,
    "cache_hit_rate": 0.0,
    "queue_depth": 12
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
