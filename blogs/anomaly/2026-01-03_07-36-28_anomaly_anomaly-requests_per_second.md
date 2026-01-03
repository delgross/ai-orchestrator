---
timestamp: 1767443788.907138
datetime: '2026-01-03T07:36:28.907138'
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
  anomaly_id: requests_per_second_1767443788.907138
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.283333333333333
    baseline_value: 11.433333333333334
    deviation: 2.2500000000000133
    severity: warning
    percentage_change: -1.3119533527696825
  system_state:
    active_requests: 6
    completed_requests_1min: 677
    error_rate_1min: 0.0
    avg_response_time_1min: 537.516306210832
  metadata: {}
  efficiency:
    requests_per_second: 11.283333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.28
- **Baseline Value**: 11.43
- **Deviation**: 2.25 standard deviations
- **Change**: -1.3%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 677
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 537.52ms

### Efficiency Metrics

- **Requests/sec**: 11.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.283333333333333,
    "baseline_value": 11.433333333333334,
    "deviation": 2.2500000000000133,
    "severity": "warning",
    "percentage_change": -1.3119533527696825
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 677,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 537.516306210832
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.283333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
