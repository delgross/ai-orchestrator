---
timestamp: 1767425570.621099
datetime: '2026-01-03T02:32:50.621099'
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
  anomaly_id: avg_response_time_1min_1767425570.621099
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 632.3899775561985
    baseline_value: 529.6312898290114
    deviation: 1.606043931465048
    severity: warning
    percentage_change: 19.401929172342168
  system_state:
    active_requests: 6
    completed_requests_1min: 821
    error_rate_1min: 0.0
    avg_response_time_1min: 632.3899775561985
  metadata: {}
  efficiency:
    requests_per_second: 13.683333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 632.39
- **Baseline Value**: 529.63
- **Deviation**: 1.61 standard deviations
- **Change**: +19.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 821
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 632.39ms

### Efficiency Metrics

- **Requests/sec**: 13.68
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 632.3899775561985,
    "baseline_value": 529.6312898290114,
    "deviation": 1.606043931465048,
    "severity": "warning",
    "percentage_change": 19.401929172342168
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 821,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 632.3899775561985
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.683333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
