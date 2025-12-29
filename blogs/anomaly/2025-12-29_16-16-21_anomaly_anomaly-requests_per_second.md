---
timestamp: 1767042981.7796512
datetime: '2025-12-29T16:16:21.779651'
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
  anomaly_id: requests_per_second_1767042981.7796512
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.2833333333333333
    baseline_value: 0.026234567901234566
    deviation: 6.189768373618651
    severity: critical
    percentage_change: 980.0000000000001
  system_state:
    active_requests: 1
    completed_requests_1min: 17
    error_rate_1min: 0.0
    avg_response_time_1min: 1629.8737946678611
  metadata: {}
  efficiency:
    requests_per_second: 0.2833333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.28
- **Baseline Value**: 0.03
- **Deviation**: 6.19 standard deviations
- **Change**: +980.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 17
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1629.87ms

### Efficiency Metrics

- **Requests/sec**: 0.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 0.2833333333333333,
    "baseline_value": 0.026234567901234566,
    "deviation": 6.189768373618651,
    "severity": "critical",
    "percentage_change": 980.0000000000001
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 17,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1629.8737946678611
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.2833333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
