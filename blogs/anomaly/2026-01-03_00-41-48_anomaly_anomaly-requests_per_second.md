---
timestamp: 1767418908.7032478
datetime: '2026-01-03T00:41:48.703248'
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
  anomaly_id: requests_per_second_1767418908.7032478
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 28.416666666666668
    baseline_value: 33.78333333333333
    deviation: 4.472222222222209
    severity: critical
    percentage_change: -15.885545140601867
  system_state:
    active_requests: 32
    completed_requests_1min: 1705
    error_rate_1min: 0.0
    avg_response_time_1min: 1082.5365158819384
  metadata: {}
  efficiency:
    requests_per_second: 28.416666666666668
    cache_hit_rate: 0.0
    queue_depth: 32
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 28.42
- **Baseline Value**: 33.78
- **Deviation**: 4.47 standard deviations
- **Change**: -15.9%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 32
- **Completed Requests (1min)**: 1705
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1082.54ms

### Efficiency Metrics

- **Requests/sec**: 28.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 32

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 28.416666666666668,
    "baseline_value": 33.78333333333333,
    "deviation": 4.472222222222209,
    "severity": "critical",
    "percentage_change": -15.885545140601867
  },
  "system_state": {
    "active_requests": 32,
    "completed_requests_1min": 1705,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1082.5365158819384
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 28.416666666666668,
    "cache_hit_rate": 0.0,
    "queue_depth": 32
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
