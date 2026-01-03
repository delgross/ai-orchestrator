---
timestamp: 1767376965.901349
datetime: '2026-01-02T13:02:45.901349'
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
  anomaly_id: avg_response_time_1min_1767376965.901349
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1235.073509430476
    baseline_value: 958.9037231332966
    deviation: 2.3535123975694785
    severity: warning
    percentage_change: 28.800575035288418
  system_state:
    active_requests: 8
    completed_requests_1min: 757
    error_rate_1min: 0.0
    avg_response_time_1min: 1235.073509430476
  metadata: {}
  efficiency:
    requests_per_second: 12.616666666666667
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1235.07
- **Baseline Value**: 958.90
- **Deviation**: 2.35 standard deviations
- **Change**: +28.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 757
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1235.07ms

### Efficiency Metrics

- **Requests/sec**: 12.62
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1235.073509430476,
    "baseline_value": 958.9037231332966,
    "deviation": 2.3535123975694785,
    "severity": "warning",
    "percentage_change": 28.800575035288418
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 757,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1235.073509430476
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.616666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
