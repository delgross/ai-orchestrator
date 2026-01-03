---
timestamp: 1767376305.703619
datetime: '2026-01-02T12:51:45.703619'
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
  anomaly_id: requests_per_second_1767376305.703619
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.266666666666667
    baseline_value: 13.516666666666667
    deviation: 3.0000000000000426
    severity: critical
    percentage_change: -1.8495684340320588
  system_state:
    active_requests: 8
    completed_requests_1min: 796
    error_rate_1min: 0.0
    avg_response_time_1min: 514.9484135996756
  metadata: {}
  efficiency:
    requests_per_second: 13.266666666666667
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.27
- **Baseline Value**: 13.52
- **Deviation**: 3.00 standard deviations
- **Change**: -1.8%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 796
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 514.95ms

### Efficiency Metrics

- **Requests/sec**: 13.27
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
    "current_value": 13.266666666666667,
    "baseline_value": 13.516666666666667,
    "deviation": 3.0000000000000426,
    "severity": "critical",
    "percentage_change": -1.8495684340320588
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 796,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 514.9484135996756
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.266666666666667,
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
