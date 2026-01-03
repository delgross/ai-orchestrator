---
timestamp: 1767415366.982626
datetime: '2026-01-02T23:42:46.982626'
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
  anomaly_id: active_requests_1767415366.982626
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 30.0
    baseline_value: 10.0
    deviation: 2.0
    severity: warning
    percentage_change: 200.0
  system_state:
    active_requests: 30
    completed_requests_1min: 490
    error_rate_1min: 0.0
    avg_response_time_1min: 2710.2158288566434
  metadata: {}
  efficiency:
    requests_per_second: 8.166666666666666
    cache_hit_rate: 0.0
    queue_depth: 30
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 30.00
- **Baseline Value**: 10.00
- **Deviation**: 2.00 standard deviations
- **Change**: +200.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 30
- **Completed Requests (1min)**: 490
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2710.22ms

### Efficiency Metrics

- **Requests/sec**: 8.17
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 30

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 30.0,
    "baseline_value": 10.0,
    "deviation": 2.0,
    "severity": "warning",
    "percentage_change": 200.0
  },
  "system_state": {
    "active_requests": 30,
    "completed_requests_1min": 490,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2710.2158288566434
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 8.166666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 30
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
