---
timestamp: 1767420049.1771798
datetime: '2026-01-03T01:00:49.177180'
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
  anomaly_id: active_requests_1767420049.1771798
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 24.0
    baseline_value: 27.0
    deviation: 3.0
    severity: critical
    percentage_change: -11.11111111111111
  system_state:
    active_requests: 24
    completed_requests_1min: 2472
    error_rate_1min: 0.0
    avg_response_time_1min: 662.5729333428503
  metadata: {}
  efficiency:
    requests_per_second: 41.2
    cache_hit_rate: 0.0
    queue_depth: 24
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 24.00
- **Baseline Value**: 27.00
- **Deviation**: 3.00 standard deviations
- **Change**: -11.1%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 24
- **Completed Requests (1min)**: 2472
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 662.57ms

### Efficiency Metrics

- **Requests/sec**: 41.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 24

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 24.0,
    "baseline_value": 27.0,
    "deviation": 3.0,
    "severity": "critical",
    "percentage_change": -11.11111111111111
  },
  "system_state": {
    "active_requests": 24,
    "completed_requests_1min": 2472,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 662.5729333428503
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 41.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 24
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
