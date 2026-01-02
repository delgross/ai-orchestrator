---
timestamp: 1767270528.3518772
datetime: '2026-01-01T07:28:48.351877'
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
  anomaly_id: avg_response_time_1min_1767270528.3518772
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 548.6774444580078
    baseline_value: 321.86423815213715
    deviation: 2.8182504780584923
    severity: warning
    percentage_change: 70.46859496041985
  system_state:
    active_requests: 1
    completed_requests_1min: 67
    error_rate_1min: 0.0
    avg_response_time_1min: 548.6774444580078
  metadata: {}
  efficiency:
    requests_per_second: 1.1166666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 548.68
- **Baseline Value**: 321.86
- **Deviation**: 2.82 standard deviations
- **Change**: +70.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 67
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 548.68ms

### Efficiency Metrics

- **Requests/sec**: 1.12
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 548.6774444580078,
    "baseline_value": 321.86423815213715,
    "deviation": 2.8182504780584923,
    "severity": "warning",
    "percentage_change": 70.46859496041985
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 67,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 548.6774444580078
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.1166666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
