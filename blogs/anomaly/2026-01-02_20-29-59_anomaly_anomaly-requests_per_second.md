---
timestamp: 1767403799.9348989
datetime: '2026-01-02T20:29:59.934899'
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
  anomaly_id: requests_per_second_1767403799.9348989
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 8.516666666666667
    baseline_value: 13.566666666666666
    deviation: 21.64285714285705
    severity: critical
    percentage_change: -37.22358722358722
  system_state:
    active_requests: 3
    completed_requests_1min: 511
    error_rate_1min: 0.0
    avg_response_time_1min: 431.291302589521
  metadata: {}
  efficiency:
    requests_per_second: 8.516666666666667
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 8.52
- **Baseline Value**: 13.57
- **Deviation**: 21.64 standard deviations
- **Change**: -37.2%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 511
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 431.29ms

### Efficiency Metrics

- **Requests/sec**: 8.52
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
    "current_value": 8.516666666666667,
    "baseline_value": 13.566666666666666,
    "deviation": 21.64285714285705,
    "severity": "critical",
    "percentage_change": -37.22358722358722
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 511,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 431.291302589521
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 8.516666666666667,
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
