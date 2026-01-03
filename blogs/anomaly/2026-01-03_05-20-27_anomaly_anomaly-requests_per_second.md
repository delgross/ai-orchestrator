---
timestamp: 1767435627.117576
datetime: '2026-01-03T05:20:27.117576'
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
  anomaly_id: requests_per_second_1767435627.117576
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.716666666666667
    baseline_value: 11.25
    deviation: 3.999999999999985
    severity: critical
    percentage_change: 4.14814814814815
  system_state:
    active_requests: 7
    completed_requests_1min: 703
    error_rate_1min: 0.0
    avg_response_time_1min: 551.3388188092163
  metadata: {}
  efficiency:
    requests_per_second: 11.716666666666667
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.72
- **Baseline Value**: 11.25
- **Deviation**: 4.00 standard deviations
- **Change**: +4.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 703
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 551.34ms

### Efficiency Metrics

- **Requests/sec**: 11.72
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.716666666666667,
    "baseline_value": 11.25,
    "deviation": 3.999999999999985,
    "severity": "critical",
    "percentage_change": 4.14814814814815
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 703,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 551.3388188092163
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.716666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
