---
timestamp: 1766955677.74576
datetime: '2025-12-28T16:01:17.745760'
category: anomaly
severity: warning
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: requests_per_second_1766955677.74576
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.8833333333333333
    baseline_value: 0.14750656167979004
    deviation: 4.050800448235304
    severity: warning
    percentage_change: 1176.7793594306047
  system_state:
    active_requests: 1
    completed_requests_1min: 113
    error_rate_1min: 0.0
    avg_response_time_1min: 145.44192246631184
  metadata: {}
  efficiency:
    requests_per_second: 1.8833333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.88
- **Baseline Value**: 0.15
- **Deviation**: 4.05 standard deviations
- **Change**: +1176.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 113
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 145.44ms

### Efficiency Metrics

- **Requests/sec**: 1.88
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.8833333333333333,
    "baseline_value": 0.14750656167979004,
    "deviation": 4.050800448235304,
    "severity": "warning",
    "percentage_change": 1176.7793594306047
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 113,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 145.44192246631184
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.8833333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
