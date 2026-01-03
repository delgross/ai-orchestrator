---
timestamp: 1767413325.551102
datetime: '2026-01-02T23:08:45.551102'
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
  anomaly_id: active_requests_1767413325.551102
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 13.0
    baseline_value: 2.0
    deviation: 5.5
    severity: critical
    percentage_change: 550.0
  system_state:
    active_requests: 13
    completed_requests_1min: 1643
    error_rate_1min: 0.0
    avg_response_time_1min: 344.88454085621106
  metadata: {}
  efficiency:
    requests_per_second: 27.383333333333333
    cache_hit_rate: 0.0
    queue_depth: 13
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 13.00
- **Baseline Value**: 2.00
- **Deviation**: 5.50 standard deviations
- **Change**: +550.0%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 13
- **Completed Requests (1min)**: 1643
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 344.88ms

### Efficiency Metrics

- **Requests/sec**: 27.38
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 13

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 13.0,
    "baseline_value": 2.0,
    "deviation": 5.5,
    "severity": "critical",
    "percentage_change": 550.0
  },
  "system_state": {
    "active_requests": 13,
    "completed_requests_1min": 1643,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 344.88454085621106
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 27.383333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 13
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
