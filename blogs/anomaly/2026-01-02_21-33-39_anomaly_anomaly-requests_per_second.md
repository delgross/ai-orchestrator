---
timestamp: 1767407619.10798
datetime: '2026-01-02T21:33:39.107980'
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
  anomaly_id: requests_per_second_1767407619.10798
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.116666666666667
    baseline_value: 13.783333333333333
    deviation: 14.285714285714223
    severity: critical
    percentage_change: -12.0918984280532
  system_state:
    active_requests: 6
    completed_requests_1min: 727
    error_rate_1min: 0.0
    avg_response_time_1min: 492.84610033363225
  metadata: {}
  efficiency:
    requests_per_second: 12.116666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.12
- **Baseline Value**: 13.78
- **Deviation**: 14.29 standard deviations
- **Change**: -12.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 727
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 492.85ms

### Efficiency Metrics

- **Requests/sec**: 12.12
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.116666666666667,
    "baseline_value": 13.783333333333333,
    "deviation": 14.285714285714223,
    "severity": "critical",
    "percentage_change": -12.0918984280532
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 727,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 492.84610033363225
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.116666666666667,
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
