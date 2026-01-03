---
timestamp: 1767449610.07216
datetime: '2026-01-03T09:13:30.072160'
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
  anomaly_id: requests_per_second_1767449610.07216
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.583333333333333
    baseline_value: 11.183333333333334
    deviation: 37.33333333333325
    severity: critical
    percentage_change: -50.074515648286145
  system_state:
    active_requests: 0
    completed_requests_1min: 335
    error_rate_1min: 0.0
    avg_response_time_1min: 558.4532239543857
  metadata: {}
  efficiency:
    requests_per_second: 5.583333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.58
- **Baseline Value**: 11.18
- **Deviation**: 37.33 standard deviations
- **Change**: -50.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 335
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 558.45ms

### Efficiency Metrics

- **Requests/sec**: 5.58
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
    "current_value": 5.583333333333333,
    "baseline_value": 11.183333333333334,
    "deviation": 37.33333333333325,
    "severity": "critical",
    "percentage_change": -50.074515648286145
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 335,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 558.4532239543857
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.583333333333333,
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
