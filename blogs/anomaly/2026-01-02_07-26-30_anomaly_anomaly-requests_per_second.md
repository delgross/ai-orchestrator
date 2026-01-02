---
timestamp: 1767356790.814684
datetime: '2026-01-02T07:26:30.814684'
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
  anomaly_id: requests_per_second_1767356790.814684
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.783333333333333
    baseline_value: 12.533333333333333
    deviation: 7.941176470588239
    severity: critical
    percentage_change: -53.8563829787234
  system_state:
    active_requests: 5
    completed_requests_1min: 347
    error_rate_1min: 0.0
    avg_response_time_1min: 624.2242340395704
  metadata: {}
  efficiency:
    requests_per_second: 5.783333333333333
    cache_hit_rate: 0.0
    queue_depth: 5
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.78
- **Baseline Value**: 12.53
- **Deviation**: 7.94 standard deviations
- **Change**: -53.9%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 5
- **Completed Requests (1min)**: 347
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 624.22ms

### Efficiency Metrics

- **Requests/sec**: 5.78
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 5

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 5.783333333333333,
    "baseline_value": 12.533333333333333,
    "deviation": 7.941176470588239,
    "severity": "critical",
    "percentage_change": -53.8563829787234
  },
  "system_state": {
    "active_requests": 5,
    "completed_requests_1min": 347,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 624.2242340395704
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.783333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 5
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
