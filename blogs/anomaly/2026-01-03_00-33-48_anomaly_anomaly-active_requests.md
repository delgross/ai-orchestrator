---
timestamp: 1767418428.518259
datetime: '2026-01-03T00:33:48.518259'
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
  anomaly_id: active_requests_1767418428.518259
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 25.0
    baseline_value: 29.0
    deviation: 2.0
    severity: warning
    percentage_change: -13.793103448275861
  system_state:
    active_requests: 25
    completed_requests_1min: 1877
    error_rate_1min: 0.0
    avg_response_time_1min: 758.6240314967339
  metadata: {}
  efficiency:
    requests_per_second: 31.283333333333335
    cache_hit_rate: 0.0
    queue_depth: 25
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 25.00
- **Baseline Value**: 29.00
- **Deviation**: 2.00 standard deviations
- **Change**: -13.8%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 25
- **Completed Requests (1min)**: 1877
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 758.62ms

### Efficiency Metrics

- **Requests/sec**: 31.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 25

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 25.0,
    "baseline_value": 29.0,
    "deviation": 2.0,
    "severity": "warning",
    "percentage_change": -13.793103448275861
  },
  "system_state": {
    "active_requests": 25,
    "completed_requests_1min": 1877,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 758.6240314967339
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 31.283333333333335,
    "cache_hit_rate": 0.0,
    "queue_depth": 25
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
