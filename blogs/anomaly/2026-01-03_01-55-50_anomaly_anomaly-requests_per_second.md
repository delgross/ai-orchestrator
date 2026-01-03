---
timestamp: 1767423350.026722
datetime: '2026-01-03T01:55:50.026722'
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
  anomaly_id: requests_per_second_1767423350.026722
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.633333333333333
    baseline_value: 13.866666666666667
    deviation: 1.5555555555555582
    severity: warning
    percentage_change: -1.6826923076923146
  system_state:
    active_requests: 8
    completed_requests_1min: 818
    error_rate_1min: 0.0
    avg_response_time_1min: 565.9672170513126
  metadata: {}
  efficiency:
    requests_per_second: 13.633333333333333
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.63
- **Baseline Value**: 13.87
- **Deviation**: 1.56 standard deviations
- **Change**: -1.7%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 818
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 565.97ms

### Efficiency Metrics

- **Requests/sec**: 13.63
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.633333333333333,
    "baseline_value": 13.866666666666667,
    "deviation": 1.5555555555555582,
    "severity": "warning",
    "percentage_change": -1.6826923076923146
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 818,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 565.9672170513126
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.633333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
