---
timestamp: 1767323620.747179
datetime: '2026-01-01T22:13:40.747179'
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
  anomaly_id: requests_per_second_1767323620.747179
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.283333333333333
    baseline_value: 13.4
    deviation: 1.7500000000000133
    severity: warning
    percentage_change: -0.8706467661691577
  system_state:
    active_requests: 6
    completed_requests_1min: 797
    error_rate_1min: 0.0
    avg_response_time_1min: 450.1577506549984
  metadata: {}
  efficiency:
    requests_per_second: 13.283333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.28
- **Baseline Value**: 13.40
- **Deviation**: 1.75 standard deviations
- **Change**: -0.9%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 797
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 450.16ms

### Efficiency Metrics

- **Requests/sec**: 13.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.283333333333333,
    "baseline_value": 13.4,
    "deviation": 1.7500000000000133,
    "severity": "warning",
    "percentage_change": -0.8706467661691577
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 797,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 450.1577506549984
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.283333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
