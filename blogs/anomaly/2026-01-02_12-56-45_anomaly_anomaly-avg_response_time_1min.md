---
timestamp: 1767376605.808466
datetime: '2026-01-02T12:56:45.808466'
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
  anomaly_id: avg_response_time_1min_1767376605.808466
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 643.277652257145
    baseline_value: 517.4743119519115
    deviation: 2.6395730992296955
    severity: warning
    percentage_change: 24.31103098252425
  system_state:
    active_requests: 9
    completed_requests_1min: 734
    error_rate_1min: 0.0
    avg_response_time_1min: 643.277652257145
  metadata: {}
  efficiency:
    requests_per_second: 12.233333333333333
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 643.28
- **Baseline Value**: 517.47
- **Deviation**: 2.64 standard deviations
- **Change**: +24.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 734
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 643.28ms

### Efficiency Metrics

- **Requests/sec**: 12.23
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 643.277652257145,
    "baseline_value": 517.4743119519115,
    "deviation": 2.6395730992296955,
    "severity": "warning",
    "percentage_change": 24.31103098252425
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 734,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 643.277652257145
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.233333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
