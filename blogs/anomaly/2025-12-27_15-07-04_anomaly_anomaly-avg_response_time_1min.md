---
timestamp: 1766866024.202332
datetime: '2025-12-27T15:07:04.202332'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: avg_response_time_1min_1766866024.202332
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 6.594702882586785
    baseline_value: 124.32678859043598
    deviation: 5.976950238892172
    severity: warning
    percentage_change: -94.69567021125961
  system_state:
    active_requests: 0
    completed_requests_1min: 53
    error_rate_1min: 0.0
    avg_response_time_1min: 6.594702882586785
  metadata: {}
  efficiency:
    requests_per_second: 0.8833333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 6.59
- **Baseline Value**: 124.33
- **Deviation**: 5.98 standard deviations
- **Change**: -94.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 53
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 6.59ms

### Efficiency Metrics

- **Requests/sec**: 0.88
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 6.594702882586785,
    "baseline_value": 124.32678859043598,
    "deviation": 5.976950238892172,
    "severity": "warning",
    "percentage_change": -94.69567021125961
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 53,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 6.594702882586785
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.8833333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
