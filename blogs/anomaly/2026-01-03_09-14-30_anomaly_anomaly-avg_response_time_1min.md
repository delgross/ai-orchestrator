---
timestamp: 1767449670.105338
datetime: '2026-01-03T09:14:30.105338'
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
  anomaly_id: avg_response_time_1min_1767449670.105338
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 275.6741108565495
    baseline_value: 540.7942584108993
    deviation: 23.761167744847807
    severity: critical
    percentage_change: -49.02421640595704
  system_state:
    active_requests: 1
    completed_requests_1min: 116
    error_rate_1min: 0.0
    avg_response_time_1min: 275.6741108565495
  metadata: {}
  efficiency:
    requests_per_second: 1.9333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 275.67
- **Baseline Value**: 540.79
- **Deviation**: 23.76 standard deviations
- **Change**: -49.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 116
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 275.67ms

### Efficiency Metrics

- **Requests/sec**: 1.93
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 275.6741108565495,
    "baseline_value": 540.7942584108993,
    "deviation": 23.761167744847807,
    "severity": "critical",
    "percentage_change": -49.02421640595704
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 116,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 275.6741108565495
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.9333333333333333,
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
