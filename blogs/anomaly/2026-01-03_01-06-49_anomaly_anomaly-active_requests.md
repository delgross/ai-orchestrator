---
timestamp: 1767420409.2478971
datetime: '2026-01-03T01:06:49.247897'
category: anomaly
severity: critical
title: 'Anomaly: active_requests'
source: anomaly_detector
tags:
- anomaly
- active_requests
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: active_requests_1767420409.2478971
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 18.0
    baseline_value: 25.0
    deviation: 7.0
    severity: critical
    percentage_change: -28.000000000000004
  system_state:
    active_requests: 18
    completed_requests_1min: 2522
    error_rate_1min: 0.0
    avg_response_time_1min: 583.1304088081281
  metadata: {}
  efficiency:
    requests_per_second: 42.03333333333333
    cache_hit_rate: 0.0
    queue_depth: 18
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 18.00
- **Baseline Value**: 25.00
- **Deviation**: 7.00 standard deviations
- **Change**: -28.0%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 18
- **Completed Requests (1min)**: 2522
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 583.13ms

### Efficiency Metrics

- **Requests/sec**: 42.03
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 18

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 18.0,
    "baseline_value": 25.0,
    "deviation": 7.0,
    "severity": "critical",
    "percentage_change": -28.000000000000004
  },
  "system_state": {
    "active_requests": 18,
    "completed_requests_1min": 2522,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 583.1304088081281
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 42.03333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 18
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
