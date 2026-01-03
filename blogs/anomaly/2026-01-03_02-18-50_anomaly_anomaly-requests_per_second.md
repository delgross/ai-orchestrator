---
timestamp: 1767424730.476523
datetime: '2026-01-03T02:18:50.476523'
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
  anomaly_id: requests_per_second_1767424730.476523
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.983333333333333
    baseline_value: 14.233333333333333
    deviation: 1.8749999999999818
    severity: warning
    percentage_change: -1.7564402810304451
  system_state:
    active_requests: 7
    completed_requests_1min: 839
    error_rate_1min: 0.0
    avg_response_time_1min: 517.9522759297749
  metadata: {}
  efficiency:
    requests_per_second: 13.983333333333333
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.98
- **Baseline Value**: 14.23
- **Deviation**: 1.87 standard deviations
- **Change**: -1.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 839
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 517.95ms

### Efficiency Metrics

- **Requests/sec**: 13.98
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.983333333333333,
    "baseline_value": 14.233333333333333,
    "deviation": 1.8749999999999818,
    "severity": "warning",
    "percentage_change": -1.7564402810304451
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 839,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 517.9522759297749
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.983333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
