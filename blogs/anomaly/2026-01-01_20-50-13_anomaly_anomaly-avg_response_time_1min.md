---
timestamp: 1767318613.528202
datetime: '2026-01-01T20:50:13.528202'
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
  anomaly_id: avg_response_time_1min_1767318613.528202
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 108.61422070141496
    baseline_value: 186.67097144074492
    deviation: 2.5186238918495145
    severity: warning
    percentage_change: -41.81515215616026
  system_state:
    active_requests: 1
    completed_requests_1min: 348
    error_rate_1min: 0.0
    avg_response_time_1min: 108.61422070141496
  metadata: {}
  efficiency:
    requests_per_second: 5.8
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 108.61
- **Baseline Value**: 186.67
- **Deviation**: 2.52 standard deviations
- **Change**: -41.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 348
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 108.61ms

### Efficiency Metrics

- **Requests/sec**: 5.80
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 108.61422070141496,
    "baseline_value": 186.67097144074492,
    "deviation": 2.5186238918495145,
    "severity": "warning",
    "percentage_change": -41.81515215616026
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 348,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 108.61422070141496
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.8,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
