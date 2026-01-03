---
timestamp: 1767438627.704294
datetime: '2026-01-03T06:10:27.704294'
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
  anomaly_id: avg_response_time_1min_1767438627.704294
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 581.1095038758888
    baseline_value: 547.2595914059093
    deviation: 3.1275030998558684
    severity: critical
    percentage_change: 6.185348416282496
  system_state:
    active_requests: 7
    completed_requests_1min: 683
    error_rate_1min: 0.0
    avg_response_time_1min: 581.1095038758888
  metadata: {}
  efficiency:
    requests_per_second: 11.383333333333333
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 581.11
- **Baseline Value**: 547.26
- **Deviation**: 3.13 standard deviations
- **Change**: +6.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 683
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 581.11ms

### Efficiency Metrics

- **Requests/sec**: 11.38
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 581.1095038758888,
    "baseline_value": 547.2595914059093,
    "deviation": 3.1275030998558684,
    "severity": "critical",
    "percentage_change": 6.185348416282496
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 683,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 581.1095038758888
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.383333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
