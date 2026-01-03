---
timestamp: 1767374985.455363
datetime: '2026-01-02T12:29:45.455363'
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
  anomaly_id: avg_response_time_1min_1767374985.455363
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1042.1596117272154
    baseline_value: 660.6112926237045
    deviation: 2.2190516757243177
    severity: warning
    percentage_change: 57.75685692385635
  system_state:
    active_requests: 3
    completed_requests_1min: 491
    error_rate_1min: 0.0
    avg_response_time_1min: 1042.1596117272154
  metadata: {}
  efficiency:
    requests_per_second: 8.183333333333334
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1042.16
- **Baseline Value**: 660.61
- **Deviation**: 2.22 standard deviations
- **Change**: +57.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 491
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1042.16ms

### Efficiency Metrics

- **Requests/sec**: 8.18
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1042.1596117272154,
    "baseline_value": 660.6112926237045,
    "deviation": 2.2190516757243177,
    "severity": "warning",
    "percentage_change": 57.75685692385635
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 491,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1042.1596117272154
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 8.183333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
