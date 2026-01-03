---
timestamp: 1767445649.216279
datetime: '2026-01-03T08:07:29.216279'
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
  anomaly_id: avg_response_time_1min_1767445649.216279
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 345.80599304533354
    baseline_value: 504.3061263703836
    deviation: 4.18169143951721
    severity: critical
    percentage_change: -31.429349166510207
  system_state:
    active_requests: 1
    completed_requests_1min: 137
    error_rate_1min: 0.0
    avg_response_time_1min: 345.80599304533354
  metadata: {}
  efficiency:
    requests_per_second: 2.283333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 345.81
- **Baseline Value**: 504.31
- **Deviation**: 4.18 standard deviations
- **Change**: -31.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 137
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 345.81ms

### Efficiency Metrics

- **Requests/sec**: 2.28
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
    "current_value": 345.80599304533354,
    "baseline_value": 504.3061263703836,
    "deviation": 4.18169143951721,
    "severity": "critical",
    "percentage_change": -31.429349166510207
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 137,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 345.80599304533354
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.283333333333333,
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
