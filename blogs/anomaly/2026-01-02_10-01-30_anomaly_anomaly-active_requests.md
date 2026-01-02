---
timestamp: 1767366090.383529
datetime: '2026-01-02T10:01:30.383529'
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
  anomaly_id: active_requests_1767366090.383529
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 14.0
    baseline_value: 11.0
    deviation: 1.5
    severity: warning
    percentage_change: 27.27272727272727
  system_state:
    active_requests: 14
    completed_requests_1min: 23
    error_rate_1min: 0.0
    avg_response_time_1min: 13249.22485973524
  metadata: {}
  efficiency:
    requests_per_second: 0.38333333333333336
    cache_hit_rate: 0.0
    queue_depth: 14
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 14.00
- **Baseline Value**: 11.00
- **Deviation**: 1.50 standard deviations
- **Change**: +27.3%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 14
- **Completed Requests (1min)**: 23
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 13249.22ms

### Efficiency Metrics

- **Requests/sec**: 0.38
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 14

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 14.0,
    "baseline_value": 11.0,
    "deviation": 1.5,
    "severity": "warning",
    "percentage_change": 27.27272727272727
  },
  "system_state": {
    "active_requests": 14,
    "completed_requests_1min": 23,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 13249.22485973524
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.38333333333333336,
    "cache_hit_rate": 0.0,
    "queue_depth": 14
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
