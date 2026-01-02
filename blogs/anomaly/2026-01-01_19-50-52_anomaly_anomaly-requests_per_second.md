---
timestamp: 1767315052.311404
datetime: '2026-01-01T19:50:52.311404'
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
  anomaly_id: requests_per_second_1767315052.311404
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 6.433333333333334
    baseline_value: 1.9333333333333333
    deviation: 5.000000000000001
    severity: critical
    percentage_change: 232.75862068965517
  system_state:
    active_requests: 1
    completed_requests_1min: 386
    error_rate_1min: 0.0
    avg_response_time_1min: 214.5533709946074
  metadata: {}
  efficiency:
    requests_per_second: 6.433333333333334
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 6.43
- **Baseline Value**: 1.93
- **Deviation**: 5.00 standard deviations
- **Change**: +232.8%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 386
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 214.55ms

### Efficiency Metrics

- **Requests/sec**: 6.43
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 6.433333333333334,
    "baseline_value": 1.9333333333333333,
    "deviation": 5.000000000000001,
    "severity": "critical",
    "percentage_change": 232.75862068965517
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 386,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 214.5533709946074
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.433333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
