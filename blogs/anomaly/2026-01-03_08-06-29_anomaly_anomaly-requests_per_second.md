---
timestamp: 1767445589.181931
datetime: '2026-01-03T08:06:29.181931'
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
  anomaly_id: requests_per_second_1767445589.181931
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 8.15
    baseline_value: 11.966666666666667
    deviation: 45.79999999999967
    severity: critical
    percentage_change: -31.894150417827294
  system_state:
    active_requests: 0
    completed_requests_1min: 489
    error_rate_1min: 0.0
    avg_response_time_1min: 511.53077425888466
  metadata: {}
  efficiency:
    requests_per_second: 8.15
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 8.15
- **Baseline Value**: 11.97
- **Deviation**: 45.80 standard deviations
- **Change**: -31.9%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 489
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 511.53ms

### Efficiency Metrics

- **Requests/sec**: 8.15
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
    "current_value": 8.15,
    "baseline_value": 11.966666666666667,
    "deviation": 45.79999999999967,
    "severity": "critical",
    "percentage_change": -31.894150417827294
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 489,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 511.53077425888466
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 8.15,
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
