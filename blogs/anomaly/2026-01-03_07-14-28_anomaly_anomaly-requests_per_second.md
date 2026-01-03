---
timestamp: 1767442468.670479
datetime: '2026-01-03T07:14:28.670479'
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
  anomaly_id: requests_per_second_1767442468.670479
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 10.883333333333333
    baseline_value: 11.1
    deviation: 2.1666666666666754
    severity: warning
    percentage_change: -1.951951951951953
  system_state:
    active_requests: 6
    completed_requests_1min: 653
    error_rate_1min: 0.0
    avg_response_time_1min: 585.7211517520922
  metadata: {}
  efficiency:
    requests_per_second: 10.883333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 10.88
- **Baseline Value**: 11.10
- **Deviation**: 2.17 standard deviations
- **Change**: -2.0%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 653
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 585.72ms

### Efficiency Metrics

- **Requests/sec**: 10.88
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 10.883333333333333,
    "baseline_value": 11.1,
    "deviation": 2.1666666666666754,
    "severity": "warning",
    "percentage_change": -1.951951951951953
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 653,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 585.7211517520922
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.883333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
