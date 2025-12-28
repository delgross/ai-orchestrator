---
timestamp: 1766865904.191316
datetime: '2025-12-27T15:05:04.191316'
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
  anomaly_id: requests_per_second_1766865904.191316
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.8833333333333333
    baseline_value: 2.3857166666666667
    deviation: 6.992985102693597
    severity: critical
    percentage_change: -62.97408884821473
  system_state:
    active_requests: 0
    completed_requests_1min: 53
    error_rate_1min: 0.0
    avg_response_time_1min: 6.671946003751935
  metadata: {}
  efficiency:
    requests_per_second: 0.8833333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.88
- **Baseline Value**: 2.39
- **Deviation**: 6.99 standard deviations
- **Change**: -63.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 53
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 6.67ms

### Efficiency Metrics

- **Requests/sec**: 0.88
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
    "current_value": 0.8833333333333333,
    "baseline_value": 2.3857166666666667,
    "deviation": 6.992985102693597,
    "severity": "critical",
    "percentage_change": -62.97408884821473
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 53,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 6.671946003751935
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.8833333333333333,
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
