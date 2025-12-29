---
timestamp: 1767023251.3717482
datetime: '2025-12-29T10:47:31.371748'
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
  anomaly_id: active_requests_1767023251.3717482
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 2.0
    baseline_value: 0.1076923076923077
    deviation: 5.292317558831216
    severity: warning
    percentage_change: 1757.1428571428569
  system_state:
    active_requests: 2
    completed_requests_1min: 209
    error_rate_1min: 0.0
    avg_response_time_1min: 426.3462837803307
  metadata: {}
  efficiency:
    requests_per_second: 3.4833333333333334
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 2.00
- **Baseline Value**: 0.11
- **Deviation**: 5.29 standard deviations
- **Change**: +1757.1%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 209
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 426.35ms

### Efficiency Metrics

- **Requests/sec**: 3.48
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 2.0,
    "baseline_value": 0.1076923076923077,
    "deviation": 5.292317558831216,
    "severity": "warning",
    "percentage_change": 1757.1428571428569
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 209,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 426.3462837803307
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.4833333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
