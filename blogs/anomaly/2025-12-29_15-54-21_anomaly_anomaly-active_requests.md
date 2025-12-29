---
timestamp: 1767041661.7116852
datetime: '2025-12-29T15:54:21.711685'
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
  anomaly_id: active_requests_1767041661.7116852
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 5.0
    baseline_value: 0.18211920529801323
    deviation: 5.759377166432791
    severity: warning
    percentage_change: 2645.4545454545455
  system_state:
    active_requests: 5
    completed_requests_1min: 5
    error_rate_1min: 0.0
    avg_response_time_1min: 42798.71654510498
  metadata: {}
  efficiency:
    requests_per_second: 0.08333333333333333
    cache_hit_rate: 0.0
    queue_depth: 5
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 5.00
- **Baseline Value**: 0.18
- **Deviation**: 5.76 standard deviations
- **Change**: +2645.5%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 5
- **Completed Requests (1min)**: 5
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 42798.72ms

### Efficiency Metrics

- **Requests/sec**: 0.08
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 5

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 5.0,
    "baseline_value": 0.18211920529801323,
    "deviation": 5.759377166432791,
    "severity": "warning",
    "percentage_change": 2645.4545454545455
  },
  "system_state": {
    "active_requests": 5,
    "completed_requests_1min": 5,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 42798.71654510498
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.08333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 5
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
