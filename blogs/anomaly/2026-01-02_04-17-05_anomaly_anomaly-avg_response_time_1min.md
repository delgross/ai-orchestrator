---
timestamp: 1767345425.48301
datetime: '2026-01-02T04:17:05.483010'
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
  anomaly_id: avg_response_time_1min_1767345425.48301
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 446.7113038463429
    baseline_value: 435.6570045870564
    deviation: 3.1016655983987125
    severity: critical
    percentage_change: 2.537385866150475
  system_state:
    active_requests: 6
    completed_requests_1min: 817
    error_rate_1min: 0.0
    avg_response_time_1min: 446.7113038463429
  metadata: {}
  efficiency:
    requests_per_second: 13.616666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 446.71
- **Baseline Value**: 435.66
- **Deviation**: 3.10 standard deviations
- **Change**: +2.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 817
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 446.71ms

### Efficiency Metrics

- **Requests/sec**: 13.62
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
    "current_value": 446.7113038463429,
    "baseline_value": 435.6570045870564,
    "deviation": 3.1016655983987125,
    "severity": "critical",
    "percentage_change": 2.537385866150475
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 817,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 446.7113038463429
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.616666666666667,
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
