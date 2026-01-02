---
timestamp: 1767295542.201993
datetime: '2026-01-01T14:25:42.201993'
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
  anomaly_id: requests_per_second_1767295542.201993
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 15.3
    baseline_value: 13.233333333333333
    deviation: 3.351351351351361
    severity: critical
    percentage_change: 15.617128463476082
  system_state:
    active_requests: 8
    completed_requests_1min: 918
    error_rate_1min: 0.0
    avg_response_time_1min: 694.775636938922
  metadata: {}
  efficiency:
    requests_per_second: 15.3
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 15.30
- **Baseline Value**: 13.23
- **Deviation**: 3.35 standard deviations
- **Change**: +15.6%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 918
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 694.78ms

### Efficiency Metrics

- **Requests/sec**: 15.30
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
    "current_value": 15.3,
    "baseline_value": 13.233333333333333,
    "deviation": 3.351351351351361,
    "severity": "critical",
    "percentage_change": 15.617128463476082
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 918,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 694.775636938922
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 15.3,
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
