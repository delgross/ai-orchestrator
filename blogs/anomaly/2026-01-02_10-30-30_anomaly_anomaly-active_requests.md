---
timestamp: 1767367830.7322822
datetime: '2026-01-02T10:30:30.732282'
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
  anomaly_id: active_requests_1767367830.7322822
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 14.0
    baseline_value: 16.0
    deviation: 2.0
    severity: warning
    percentage_change: -12.5
  system_state:
    active_requests: 14
    completed_requests_1min: 652
    error_rate_1min: 0.0
    avg_response_time_1min: 2077.188082267902
  metadata: {}
  efficiency:
    requests_per_second: 10.866666666666667
    cache_hit_rate: 0.0
    queue_depth: 14
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 14.00
- **Baseline Value**: 16.00
- **Deviation**: 2.00 standard deviations
- **Change**: -12.5%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 14
- **Completed Requests (1min)**: 652
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2077.19ms

### Efficiency Metrics

- **Requests/sec**: 10.87
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 14

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 14.0,
    "baseline_value": 16.0,
    "deviation": 2.0,
    "severity": "warning",
    "percentage_change": -12.5
  },
  "system_state": {
    "active_requests": 14,
    "completed_requests_1min": 652,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2077.188082267902
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.866666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 14
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
