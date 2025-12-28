---
timestamp: 1766841233.933336
datetime: '2025-12-27T08:13:53.933336'
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
  anomaly_id: active_requests_1766841233.933336
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 0.0
    baseline_value: 0.967741935483871
    deviation: 5.455095280206298
    severity: warning
    percentage_change: -100.0
  system_state:
    active_requests: 0
    completed_requests_1min: 377
    error_rate_1min: 0.0
    avg_response_time_1min: 13.11449410112214
  metadata: {}
  efficiency:
    requests_per_second: 6.283333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 0.00
- **Baseline Value**: 0.97
- **Deviation**: 5.46 standard deviations
- **Change**: -100.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 377
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 13.11ms

### Efficiency Metrics

- **Requests/sec**: 6.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 0.0,
    "baseline_value": 0.967741935483871,
    "deviation": 5.455095280206298,
    "severity": "warning",
    "percentage_change": -100.0
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 377,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 13.11449410112214
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.283333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
