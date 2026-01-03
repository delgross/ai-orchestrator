---
timestamp: 1767379008.7427998
datetime: '2026-01-02T13:36:48.742800'
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
  anomaly_id: requests_per_second_1767379008.7427998
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.116666666666667
    baseline_value: 12.783333333333333
    deviation: 2.5000000000000133
    severity: warning
    percentage_change: 2.6075619295958323
  system_state:
    active_requests: 10
    completed_requests_1min: 787
    error_rate_1min: 0.0
    avg_response_time_1min: 536.1768796453027
  metadata: {}
  efficiency:
    requests_per_second: 13.116666666666667
    cache_hit_rate: 0.0
    queue_depth: 10
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.12
- **Baseline Value**: 12.78
- **Deviation**: 2.50 standard deviations
- **Change**: +2.6%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 10
- **Completed Requests (1min)**: 787
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 536.18ms

### Efficiency Metrics

- **Requests/sec**: 13.12
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 10

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.116666666666667,
    "baseline_value": 12.783333333333333,
    "deviation": 2.5000000000000133,
    "severity": "warning",
    "percentage_change": 2.6075619295958323
  },
  "system_state": {
    "active_requests": 10,
    "completed_requests_1min": 787,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 536.1768796453027
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.116666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 10
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
