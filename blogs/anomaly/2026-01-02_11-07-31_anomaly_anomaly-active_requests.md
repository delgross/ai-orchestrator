---
timestamp: 1767370051.240491
datetime: '2026-01-02T11:07:31.240491'
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
  anomaly_id: active_requests_1767370051.240491
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 10.0
    baseline_value: 13.0
    deviation: 1.5
    severity: warning
    percentage_change: -23.076923076923077
  system_state:
    active_requests: 10
    completed_requests_1min: 728
    error_rate_1min: 0.0
    avg_response_time_1min: 1059.0674028946803
  metadata: {}
  efficiency:
    requests_per_second: 12.133333333333333
    cache_hit_rate: 0.0
    queue_depth: 10
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 10.00
- **Baseline Value**: 13.00
- **Deviation**: 1.50 standard deviations
- **Change**: -23.1%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 10
- **Completed Requests (1min)**: 728
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1059.07ms

### Efficiency Metrics

- **Requests/sec**: 12.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 10

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 10.0,
    "baseline_value": 13.0,
    "deviation": 1.5,
    "severity": "warning",
    "percentage_change": -23.076923076923077
  },
  "system_state": {
    "active_requests": 10,
    "completed_requests_1min": 728,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1059.0674028946803
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.133333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 10
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
