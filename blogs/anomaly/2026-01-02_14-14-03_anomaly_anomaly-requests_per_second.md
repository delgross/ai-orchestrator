---
timestamp: 1767381243.80599
datetime: '2026-01-02T14:14:03.805990'
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
  anomaly_id: requests_per_second_1767381243.80599
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 14.083333333333334
    baseline_value: 13.25
    deviation: 3.5714285714285867
    severity: critical
    percentage_change: 6.289308176100633
  system_state:
    active_requests: 8
    completed_requests_1min: 845
    error_rate_1min: 0.0
    avg_response_time_1min: 537.0695971878323
  metadata: {}
  efficiency:
    requests_per_second: 14.083333333333334
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 14.08
- **Baseline Value**: 13.25
- **Deviation**: 3.57 standard deviations
- **Change**: +6.3%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 845
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 537.07ms

### Efficiency Metrics

- **Requests/sec**: 14.08
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 14.083333333333334,
    "baseline_value": 13.25,
    "deviation": 3.5714285714285867,
    "severity": "critical",
    "percentage_change": 6.289308176100633
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 845,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 537.0695971878323
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.083333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
