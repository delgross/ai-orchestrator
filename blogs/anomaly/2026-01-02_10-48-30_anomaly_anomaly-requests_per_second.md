---
timestamp: 1767368910.975368
datetime: '2026-01-02T10:48:30.975368'
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
  anomaly_id: requests_per_second_1767368910.975368
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.983333333333333
    baseline_value: 10.983333333333333
    deviation: 3.0000000000000027
    severity: critical
    percentage_change: 18.20940819423369
  system_state:
    active_requests: 17
    completed_requests_1min: 779
    error_rate_1min: 0.0
    avg_response_time_1min: 1620.0101742848506
  metadata: {}
  efficiency:
    requests_per_second: 12.983333333333333
    cache_hit_rate: 0.0
    queue_depth: 17
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.98
- **Baseline Value**: 10.98
- **Deviation**: 3.00 standard deviations
- **Change**: +18.2%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 17
- **Completed Requests (1min)**: 779
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1620.01ms

### Efficiency Metrics

- **Requests/sec**: 12.98
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 17

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.983333333333333,
    "baseline_value": 10.983333333333333,
    "deviation": 3.0000000000000027,
    "severity": "critical",
    "percentage_change": 18.20940819423369
  },
  "system_state": {
    "active_requests": 17,
    "completed_requests_1min": 779,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1620.0101742848506
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.983333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 17
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
