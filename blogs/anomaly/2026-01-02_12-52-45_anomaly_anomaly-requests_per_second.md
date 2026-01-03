---
timestamp: 1767376365.7362418
datetime: '2026-01-02T12:52:45.736242'
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
  anomaly_id: requests_per_second_1767376365.7362418
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.733333333333333
    baseline_value: 13.2
    deviation: 2.5454545454545427
    severity: warning
    percentage_change: -3.535353535353537
  system_state:
    active_requests: 8
    completed_requests_1min: 764
    error_rate_1min: 0.0
    avg_response_time_1min: 672.5069527850725
  metadata: {}
  efficiency:
    requests_per_second: 12.733333333333333
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.73
- **Baseline Value**: 13.20
- **Deviation**: 2.55 standard deviations
- **Change**: -3.5%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 764
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 672.51ms

### Efficiency Metrics

- **Requests/sec**: 12.73
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.733333333333333,
    "baseline_value": 13.2,
    "deviation": 2.5454545454545427,
    "severity": "warning",
    "percentage_change": -3.535353535353537
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 764,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 672.5069527850725
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.733333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
