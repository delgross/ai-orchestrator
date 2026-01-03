---
timestamp: 1767451710.791003
datetime: '2026-01-03T09:48:30.791003'
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
  anomaly_id: avg_response_time_1min_1767451710.791003
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 933.1232176886665
    baseline_value: 473.0726330485565
    deviation: 3.5183137156370043
    severity: critical
    percentage_change: 97.24734691911254
  system_state:
    active_requests: 0
    completed_requests_1min: 9
    error_rate_1min: 0.0
    avg_response_time_1min: 933.1232176886665
  metadata: {}
  efficiency:
    requests_per_second: 0.15
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 933.12
- **Baseline Value**: 473.07
- **Deviation**: 3.52 standard deviations
- **Change**: +97.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 9
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 933.12ms

### Efficiency Metrics

- **Requests/sec**: 0.15
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 933.1232176886665,
    "baseline_value": 473.0726330485565,
    "deviation": 3.5183137156370043,
    "severity": "critical",
    "percentage_change": 97.24734691911254
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 9,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 933.1232176886665
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.15,
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
