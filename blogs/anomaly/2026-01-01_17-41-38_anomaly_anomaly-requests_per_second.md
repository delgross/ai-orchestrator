---
timestamp: 1767307298.311981
datetime: '2026-01-01T17:41:38.311981'
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
  anomaly_id: requests_per_second_1767307298.311981
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 7.033333333333333
    baseline_value: 2.216666666666667
    deviation: 36.12500000000001
    severity: critical
    percentage_change: 217.29323308270673
  system_state:
    active_requests: 2
    completed_requests_1min: 422
    error_rate_1min: 0.0
    avg_response_time_1min: 831.6097671951728
  metadata: {}
  efficiency:
    requests_per_second: 7.033333333333333
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 7.03
- **Baseline Value**: 2.22
- **Deviation**: 36.13 standard deviations
- **Change**: +217.3%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 422
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 831.61ms

### Efficiency Metrics

- **Requests/sec**: 7.03
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 7.033333333333333,
    "baseline_value": 2.216666666666667,
    "deviation": 36.12500000000001,
    "severity": "critical",
    "percentage_change": 217.29323308270673
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 422,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 831.6097671951728
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 7.033333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
