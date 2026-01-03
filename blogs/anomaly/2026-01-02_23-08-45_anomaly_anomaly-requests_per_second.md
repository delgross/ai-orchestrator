---
timestamp: 1767413325.573567
datetime: '2026-01-02T23:08:45.573567'
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
  anomaly_id: requests_per_second_1767413325.573567
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 27.366666666666667
    baseline_value: 0.08333333333333333
    deviation: 409.25000000000006
    severity: critical
    percentage_change: 32740.000000000004
  system_state:
    active_requests: 13
    completed_requests_1min: 1643
    error_rate_1min: 0.0
    avg_response_time_1min: 344.88454085621106
  metadata: {}
  efficiency:
    requests_per_second: 27.383333333333333
    cache_hit_rate: 0.0
    queue_depth: 13
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 27.37
- **Baseline Value**: 0.08
- **Deviation**: 409.25 standard deviations
- **Change**: +32740.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 13
- **Completed Requests (1min)**: 1643
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 344.88ms

### Efficiency Metrics

- **Requests/sec**: 27.38
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 13

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 27.366666666666667,
    "baseline_value": 0.08333333333333333,
    "deviation": 409.25000000000006,
    "severity": "critical",
    "percentage_change": 32740.000000000004
  },
  "system_state": {
    "active_requests": 13,
    "completed_requests_1min": 1643,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 344.88454085621106
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 27.383333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 13
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
