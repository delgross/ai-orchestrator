---
timestamp: 1766955377.698156
datetime: '2025-12-28T15:56:17.698156'
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
  anomaly_id: active_requests_1766955377.698156
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 1.0
    baseline_value: 0.03508771929824561
    deviation: 5.220993385345796
    severity: warning
    percentage_change: 2750.0
  system_state:
    active_requests: 1
    completed_requests_1min: 5
    error_rate_1min: 0.0
    avg_response_time_1min: 629.6018600463867
  metadata: {}
  efficiency:
    requests_per_second: 0.08333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 1.00
- **Baseline Value**: 0.04
- **Deviation**: 5.22 standard deviations
- **Change**: +2750.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 5
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 629.60ms

### Efficiency Metrics

- **Requests/sec**: 0.08
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 1.0,
    "baseline_value": 0.03508771929824561,
    "deviation": 5.220993385345796,
    "severity": "warning",
    "percentage_change": 2750.0
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 5,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 629.6018600463867
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.08333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
