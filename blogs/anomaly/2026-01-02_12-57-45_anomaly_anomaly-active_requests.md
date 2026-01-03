---
timestamp: 1767376665.846653
datetime: '2026-01-02T12:57:45.846653'
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
  anomaly_id: active_requests_1767376665.846653
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 12.0
    baseline_value: 10.0
    deviation: 2.0
    severity: warning
    percentage_change: 20.0
  system_state:
    active_requests: 12
    completed_requests_1min: 765
    error_rate_1min: 0.0
    avg_response_time_1min: 471.8691476809433
  metadata: {}
  efficiency:
    requests_per_second: 12.75
    cache_hit_rate: 0.0
    queue_depth: 12
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 12.00
- **Baseline Value**: 10.00
- **Deviation**: 2.00 standard deviations
- **Change**: +20.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 12
- **Completed Requests (1min)**: 765
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 471.87ms

### Efficiency Metrics

- **Requests/sec**: 12.75
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 12

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 12.0,
    "baseline_value": 10.0,
    "deviation": 2.0,
    "severity": "warning",
    "percentage_change": 20.0
  },
  "system_state": {
    "active_requests": 12,
    "completed_requests_1min": 765,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 471.8691476809433
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.75,
    "cache_hit_rate": 0.0,
    "queue_depth": 12
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
