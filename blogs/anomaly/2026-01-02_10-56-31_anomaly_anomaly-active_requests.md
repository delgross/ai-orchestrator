---
timestamp: 1767369391.140491
datetime: '2026-01-02T10:56:31.140491'
category: anomaly
severity: warning
title: 'Anomaly: active_requests'
source: anomaly_detector
tags:
- anomaly
- active_requests
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: active_requests_1767369391.140491
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 11.0
    baseline_value: 14.0
    deviation: 1.5
    severity: warning
    percentage_change: -21.428571428571427
  system_state:
    active_requests: 11
    completed_requests_1min: 631
    error_rate_1min: 0.0
    avg_response_time_1min: 2363.948067092291
  metadata: {}
  efficiency:
    requests_per_second: 10.516666666666667
    cache_hit_rate: 0.0
    queue_depth: 11
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 11.00
- **Baseline Value**: 14.00
- **Deviation**: 1.50 standard deviations
- **Change**: -21.4%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 11
- **Completed Requests (1min)**: 631
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2363.95ms

### Efficiency Metrics

- **Requests/sec**: 10.52
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 11

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 11.0,
    "baseline_value": 14.0,
    "deviation": 1.5,
    "severity": "warning",
    "percentage_change": -21.428571428571427
  },
  "system_state": {
    "active_requests": 11,
    "completed_requests_1min": 631,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2363.948067092291
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.516666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 11
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
