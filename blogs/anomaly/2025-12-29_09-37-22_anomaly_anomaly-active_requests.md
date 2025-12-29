---
timestamp: 1767019042.7381692
datetime: '2025-12-29T09:37:22.738169'
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
  anomaly_id: active_requests_1767019042.7381692
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 2.0
    baseline_value: 0.1590909090909091
    deviation: 4.640089901438262
    severity: warning
    percentage_change: 1157.142857142857
  system_state:
    active_requests: 2
    completed_requests_1min: 288
    error_rate_1min: 0.0
    avg_response_time_1min: 133.34511717160544
  metadata: {}
  efficiency:
    requests_per_second: 4.8
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 2.00
- **Baseline Value**: 0.16
- **Deviation**: 4.64 standard deviations
- **Change**: +1157.1%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 288
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 133.35ms

### Efficiency Metrics

- **Requests/sec**: 4.80
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 2.0,
    "baseline_value": 0.1590909090909091,
    "deviation": 4.640089901438262,
    "severity": "warning",
    "percentage_change": 1157.142857142857
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 288,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 133.34511717160544
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 4.8,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
