---
timestamp: 1767356370.6975732
datetime: '2026-01-02T07:19:30.697573'
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
  anomaly_id: requests_per_second_1767356370.6975732
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 17.866666666666667
    baseline_value: 13.383333333333333
    deviation: 5.274509803921572
    severity: critical
    percentage_change: 33.49937733499378
  system_state:
    active_requests: 0
    completed_requests_1min: 1072
    error_rate_1min: 0.0
    avg_response_time_1min: 113.89421415862752
  metadata: {}
  efficiency:
    requests_per_second: 17.866666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 17.87
- **Baseline Value**: 13.38
- **Deviation**: 5.27 standard deviations
- **Change**: +33.5%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 1072
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 113.89ms

### Efficiency Metrics

- **Requests/sec**: 17.87
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
    "current_value": 17.866666666666667,
    "baseline_value": 13.383333333333333,
    "deviation": 5.274509803921572,
    "severity": "critical",
    "percentage_change": 33.49937733499378
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 1072,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 113.89421415862752
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 17.866666666666667,
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
