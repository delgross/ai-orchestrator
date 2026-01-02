---
timestamp: 1767321709.353066
datetime: '2026-01-01T21:41:49.353066'
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
  anomaly_id: requests_per_second_1767321709.353066
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.733333333333333
    baseline_value: 13.25
    deviation: 3.87500000000002
    severity: critical
    percentage_change: -3.899371069182396
  system_state:
    active_requests: 6
    completed_requests_1min: 764
    error_rate_1min: 0.0
    avg_response_time_1min: 467.1515363673265
  metadata: {}
  efficiency:
    requests_per_second: 12.733333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.73
- **Baseline Value**: 13.25
- **Deviation**: 3.88 standard deviations
- **Change**: -3.9%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 764
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 467.15ms

### Efficiency Metrics

- **Requests/sec**: 12.73
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.733333333333333,
    "baseline_value": 13.25,
    "deviation": 3.87500000000002,
    "severity": "critical",
    "percentage_change": -3.899371069182396
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 764,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 467.1515363673265
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.733333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
