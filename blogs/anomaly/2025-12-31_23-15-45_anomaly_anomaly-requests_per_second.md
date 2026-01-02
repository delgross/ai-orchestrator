---
timestamp: 1767240945.904112
datetime: '2025-12-31T23:15:45.904112'
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
  anomaly_id: requests_per_second_1767240945.904112
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.566666666666666
    baseline_value: 1.0333333333333334
    deviation: 7.516703752411656
    severity: critical
    percentage_change: 438.7096774193548
  system_state:
    active_requests: 1
    completed_requests_1min: 334
    error_rate_1min: 0.0
    avg_response_time_1min: 84.56580724544868
  metadata: {}
  efficiency:
    requests_per_second: 5.566666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.57
- **Baseline Value**: 1.03
- **Deviation**: 7.52 standard deviations
- **Change**: +438.7%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 334
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 84.57ms

### Efficiency Metrics

- **Requests/sec**: 5.57
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
    "current_value": 5.566666666666666,
    "baseline_value": 1.0333333333333334,
    "deviation": 7.516703752411656,
    "severity": "critical",
    "percentage_change": 438.7096774193548
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 334,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 84.56580724544868
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.566666666666666,
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
