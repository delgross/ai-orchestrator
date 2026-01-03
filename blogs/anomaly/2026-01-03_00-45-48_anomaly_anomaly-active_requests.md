---
timestamp: 1767419148.8201962
datetime: '2026-01-03T00:45:48.820196'
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
  anomaly_id: active_requests_1767419148.8201962
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 24.0
    baseline_value: 29.0
    deviation: 2.5
    severity: warning
    percentage_change: -17.24137931034483
  system_state:
    active_requests: 24
    completed_requests_1min: 1735
    error_rate_1min: 0.0
    avg_response_time_1min: 862.8334777843024
  metadata: {}
  efficiency:
    requests_per_second: 28.916666666666668
    cache_hit_rate: 0.0
    queue_depth: 24
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 24.00
- **Baseline Value**: 29.00
- **Deviation**: 2.50 standard deviations
- **Change**: -17.2%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 24
- **Completed Requests (1min)**: 1735
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 862.83ms

### Efficiency Metrics

- **Requests/sec**: 28.92
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 24

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 24.0,
    "baseline_value": 29.0,
    "deviation": 2.5,
    "severity": "warning",
    "percentage_change": -17.24137931034483
  },
  "system_state": {
    "active_requests": 24,
    "completed_requests_1min": 1735,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 862.8334777843024
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 28.916666666666668,
    "cache_hit_rate": 0.0,
    "queue_depth": 24
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
