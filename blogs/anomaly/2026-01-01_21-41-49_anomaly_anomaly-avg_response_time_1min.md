---
timestamp: 1767321709.3410728
datetime: '2026-01-01T21:41:49.341073'
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
  anomaly_id: avg_response_time_1min_1767321709.3410728
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 467.1515363673265
    baseline_value: 451.01606845855713
    deviation: 3.626559468776322
    severity: critical
    percentage_change: 3.57758160677418
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

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 467.15
- **Baseline Value**: 451.02
- **Deviation**: 3.63 standard deviations
- **Change**: +3.6%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

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
    "metric_name": "avg_response_time_1min",
    "current_value": 467.1515363673265,
    "baseline_value": 451.01606845855713,
    "deviation": 3.626559468776322,
    "severity": "critical",
    "percentage_change": 3.57758160677418
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
