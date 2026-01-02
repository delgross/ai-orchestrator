---
timestamp: 1767306158.177042
datetime: '2026-01-01T17:22:38.177042'
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
  anomaly_id: requests_per_second_1767306158.177042
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 8.333333333333334
    baseline_value: 13.266666666666667
    deviation: 18.500000000000068
    severity: critical
    percentage_change: -37.185929648241206
  system_state:
    active_requests: 3
    completed_requests_1min: 500
    error_rate_1min: 0.0
    avg_response_time_1min: 535.761155128479
  metadata: {}
  efficiency:
    requests_per_second: 8.333333333333334
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 8.33
- **Baseline Value**: 13.27
- **Deviation**: 18.50 standard deviations
- **Change**: -37.2%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 500
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 535.76ms

### Efficiency Metrics

- **Requests/sec**: 8.33
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 8.333333333333334,
    "baseline_value": 13.266666666666667,
    "deviation": 18.500000000000068,
    "severity": "critical",
    "percentage_change": -37.185929648241206
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 500,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 535.761155128479
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 8.333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
