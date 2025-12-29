---
timestamp: 1767044361.843605
datetime: '2025-12-29T16:39:21.843605'
category: anomaly
severity: critical
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: requests_per_second_1767044361.843605
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.65
    baseline_value: 0.053794428434197884
    deviation: 7.620071982017493
    severity: critical
    percentage_change: 2967.232142857143
  system_state:
    active_requests: 0
    completed_requests_1min: 99
    error_rate_1min: 0.0
    avg_response_time_1min: 123.27478630374176
  metadata: {}
  efficiency:
    requests_per_second: 1.65
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.65
- **Baseline Value**: 0.05
- **Deviation**: 7.62 standard deviations
- **Change**: +2967.2%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 99
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 123.27ms

### Efficiency Metrics

- **Requests/sec**: 1.65
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.65,
    "baseline_value": 0.053794428434197884,
    "deviation": 7.620071982017493,
    "severity": "critical",
    "percentage_change": 2967.232142857143
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 99,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 123.27478630374176
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.65,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
