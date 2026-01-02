---
timestamp: 1767324605.803595
datetime: '2026-01-01T22:30:05.803595'
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
  anomaly_id: requests_per_second_1767324605.803595
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 6.833333333333333
    baseline_value: 13.5
    deviation: 33.33333333333346
    severity: critical
    percentage_change: -49.38271604938272
  system_state:
    active_requests: 0
    completed_requests_1min: 410
    error_rate_1min: 0.0
    avg_response_time_1min: 429.52759556654024
  metadata: {}
  efficiency:
    requests_per_second: 6.833333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 6.83
- **Baseline Value**: 13.50
- **Deviation**: 33.33 standard deviations
- **Change**: -49.4%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 410
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 429.53ms

### Efficiency Metrics

- **Requests/sec**: 6.83
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
    "current_value": 6.833333333333333,
    "baseline_value": 13.5,
    "deviation": 33.33333333333346,
    "severity": "critical",
    "percentage_change": -49.38271604938272
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 410,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 429.52759556654024
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.833333333333333,
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
