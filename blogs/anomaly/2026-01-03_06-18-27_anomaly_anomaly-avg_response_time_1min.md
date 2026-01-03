---
timestamp: 1767439107.8372312
datetime: '2026-01-03T06:18:27.837231'
category: anomaly
severity: critical
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767439107.8372312
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 567.6077606183036
    baseline_value: 533.2536239709173
    deviation: 4.000453324960185
    severity: critical
    percentage_change: 6.442363465167926
  system_state:
    active_requests: 6
    completed_requests_1min: 631
    error_rate_1min: 0.0
    avg_response_time_1min: 567.6077606183036
  metadata: {}
  efficiency:
    requests_per_second: 10.516666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 567.61
- **Baseline Value**: 533.25
- **Deviation**: 4.00 standard deviations
- **Change**: +6.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 631
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 567.61ms

### Efficiency Metrics

- **Requests/sec**: 10.52
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 567.6077606183036,
    "baseline_value": 533.2536239709173,
    "deviation": 4.000453324960185,
    "severity": "critical",
    "percentage_change": 6.442363465167926
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 631,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 567.6077606183036
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.516666666666667,
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
