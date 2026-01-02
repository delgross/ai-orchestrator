---
timestamp: 1767319350.5962749
datetime: '2026-01-01T21:02:30.596275'
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
  anomaly_id: avg_response_time_1min_1767319350.5962749
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 494.67938108745864
    baseline_value: 445.44602677100244
    deviation: 9.765183638154072
    severity: critical
    percentage_change: 11.052597028049457
  system_state:
    active_requests: 7
    completed_requests_1min: 822
    error_rate_1min: 0.0
    avg_response_time_1min: 494.67938108745864
  metadata: {}
  efficiency:
    requests_per_second: 13.7
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 494.68
- **Baseline Value**: 445.45
- **Deviation**: 9.77 standard deviations
- **Change**: +11.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 822
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 494.68ms

### Efficiency Metrics

- **Requests/sec**: 13.70
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
    "current_value": 494.67938108745864,
    "baseline_value": 445.44602677100244,
    "deviation": 9.765183638154072,
    "severity": "critical",
    "percentage_change": 11.052597028049457
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 822,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 494.67938108745864
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.7,
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
