---
timestamp: 1767413025.335972
datetime: '2026-01-02T23:03:45.335972'
category: anomaly
severity: critical
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: requests_per_second_1767413025.335972
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 10.35
    baseline_value: 0.08333333333333333
    deviation: 154.0
    severity: critical
    percentage_change: 12319.999999999998
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

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 10.35
- **Baseline Value**: 0.08
- **Deviation**: 154.00 standard deviations
- **Change**: +12320.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

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
    "metric_name": "requests_per_second",
    "current_value": 10.35,
    "baseline_value": 0.08333333333333333,
    "deviation": 154.0,
    "severity": "critical",
    "percentage_change": 12319.999999999998
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
