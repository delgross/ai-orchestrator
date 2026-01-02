---
timestamp: 1767277068.8870249
datetime: '2026-01-01T09:17:48.887025'
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
  anomaly_id: avg_response_time_1min_1767277068.8870249
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 604.6065290768942
    baseline_value: 343.47673364587735
    deviation: 2.6481892987467357
    severity: warning
    percentage_change: 76.02546835100634
  system_state:
    active_requests: 2
    completed_requests_1min: 72
    error_rate_1min: 0.0
    avg_response_time_1min: 604.6065290768942
  metadata: {}
  efficiency:
    requests_per_second: 1.2
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 604.61
- **Baseline Value**: 343.48
- **Deviation**: 2.65 standard deviations
- **Change**: +76.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 72
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 604.61ms

### Efficiency Metrics

- **Requests/sec**: 1.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 604.6065290768942,
    "baseline_value": 343.47673364587735,
    "deviation": 2.6481892987467357,
    "severity": "warning",
    "percentage_change": 76.02546835100634
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 72,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 604.6065290768942
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
