---
timestamp: 1767307598.349049
datetime: '2026-01-01T17:46:38.349049'
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
  anomaly_id: requests_per_second_1767307598.349049
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 6.883333333333334
    baseline_value: 2.316666666666667
    deviation: 18.266666666666666
    severity: critical
    percentage_change: 197.12230215827336
  system_state:
    active_requests: 3
    completed_requests_1min: 413
    error_rate_1min: 0.0
    avg_response_time_1min: 816.7845775659667
  metadata: {}
  efficiency:
    requests_per_second: 6.883333333333334
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 6.88
- **Baseline Value**: 2.32
- **Deviation**: 18.27 standard deviations
- **Change**: +197.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 413
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 816.78ms

### Efficiency Metrics

- **Requests/sec**: 6.88
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 6.883333333333334,
    "baseline_value": 2.316666666666667,
    "deviation": 18.266666666666666,
    "severity": "critical",
    "percentage_change": 197.12230215827336
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 413,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 816.7845775659667
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.883333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
