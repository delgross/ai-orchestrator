---
timestamp: 1767417167.9184499
datetime: '2026-01-03T00:12:47.918450'
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
  anomaly_id: requests_per_second_1767417167.9184499
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 30.733333333333334
    baseline_value: 35.733333333333334
    deviation: 10.344827586206875
    severity: critical
    percentage_change: -13.992537313432834
  system_state:
    active_requests: 31
    completed_requests_1min: 1844
    error_rate_1min: 0.0
    avg_response_time_1min: 962.8692024959142
  metadata: {}
  efficiency:
    requests_per_second: 30.733333333333334
    cache_hit_rate: 0.0
    queue_depth: 31
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 30.73
- **Baseline Value**: 35.73
- **Deviation**: 10.34 standard deviations
- **Change**: -14.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 31
- **Completed Requests (1min)**: 1844
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 962.87ms

### Efficiency Metrics

- **Requests/sec**: 30.73
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 31

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 30.733333333333334,
    "baseline_value": 35.733333333333334,
    "deviation": 10.344827586206875,
    "severity": "critical",
    "percentage_change": -13.992537313432834
  },
  "system_state": {
    "active_requests": 31,
    "completed_requests_1min": 1844,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 962.8692024959142
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 30.733333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 31
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
