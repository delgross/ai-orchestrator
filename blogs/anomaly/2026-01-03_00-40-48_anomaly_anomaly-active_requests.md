---
timestamp: 1767418848.633816
datetime: '2026-01-03T00:40:48.633816'
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
  anomaly_id: active_requests_1767418848.633816
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 24.0
    baseline_value: 28.0
    deviation: 2.0
    severity: warning
    percentage_change: -14.285714285714285
  system_state:
    active_requests: 24
    completed_requests_1min: 2120
    error_rate_1min: 0.0
    avg_response_time_1min: 808.0480728509291
  metadata: {}
  efficiency:
    requests_per_second: 35.333333333333336
    cache_hit_rate: 0.0
    queue_depth: 24
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 24.00
- **Baseline Value**: 28.00
- **Deviation**: 2.00 standard deviations
- **Change**: -14.3%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 24
- **Completed Requests (1min)**: 2120
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 808.05ms

### Efficiency Metrics

- **Requests/sec**: 35.33
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 24

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 24.0,
    "baseline_value": 28.0,
    "deviation": 2.0,
    "severity": "warning",
    "percentage_change": -14.285714285714285
  },
  "system_state": {
    "active_requests": 24,
    "completed_requests_1min": 2120,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 808.0480728509291
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 35.333333333333336,
    "cache_hit_rate": 0.0,
    "queue_depth": 24
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
