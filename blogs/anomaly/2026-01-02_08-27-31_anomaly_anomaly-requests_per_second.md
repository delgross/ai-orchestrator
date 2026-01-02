---
timestamp: 1767360451.9895418
datetime: '2026-01-02T08:27:31.989542'
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
  anomaly_id: requests_per_second_1767360451.9895418
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 9.8
    baseline_value: 12.533333333333333
    deviation: 3.2156862745098045
    severity: critical
    percentage_change: -21.808510638297864
  system_state:
    active_requests: 3
    completed_requests_1min: 588
    error_rate_1min: 0.0
    avg_response_time_1min: 91.56887952973243
  metadata: {}
  efficiency:
    requests_per_second: 9.8
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 9.80
- **Baseline Value**: 12.53
- **Deviation**: 3.22 standard deviations
- **Change**: -21.8%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 588
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 91.57ms

### Efficiency Metrics

- **Requests/sec**: 9.80
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
    "current_value": 9.8,
    "baseline_value": 12.533333333333333,
    "deviation": 3.2156862745098045,
    "severity": "critical",
    "percentage_change": -21.808510638297864
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 588,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 91.56887952973243
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 9.8,
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
