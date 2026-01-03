---
timestamp: 1767418488.5616078
datetime: '2026-01-03T00:34:48.561608'
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
  anomaly_id: requests_per_second_1767418488.5616078
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 28.933333333333334
    baseline_value: 32.36666666666667
    deviation: 2.641025641025647
    severity: warning
    percentage_change: -10.607621009268795
  system_state:
    active_requests: 26
    completed_requests_1min: 1736
    error_rate_1min: 0.0
    avg_response_time_1min: 831.5140967544872
  metadata: {}
  efficiency:
    requests_per_second: 28.933333333333334
    cache_hit_rate: 0.0
    queue_depth: 26
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 28.93
- **Baseline Value**: 32.37
- **Deviation**: 2.64 standard deviations
- **Change**: -10.6%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 26
- **Completed Requests (1min)**: 1736
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 831.51ms

### Efficiency Metrics

- **Requests/sec**: 28.93
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 26

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 28.933333333333334,
    "baseline_value": 32.36666666666667,
    "deviation": 2.641025641025647,
    "severity": "warning",
    "percentage_change": -10.607621009268795
  },
  "system_state": {
    "active_requests": 26,
    "completed_requests_1min": 1736,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 831.5140967544872
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 28.933333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 26
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
