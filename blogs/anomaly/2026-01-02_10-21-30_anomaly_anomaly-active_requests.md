---
timestamp: 1767367290.603901
datetime: '2026-01-02T10:21:30.603901'
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
  anomaly_id: active_requests_1767367290.603901
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 19.0
    baseline_value: 21.0
    deviation: 2.0
    severity: warning
    percentage_change: -9.523809523809524
  system_state:
    active_requests: 19
    completed_requests_1min: 670
    error_rate_1min: 0.0
    avg_response_time_1min: 1846.597831284822
  metadata: {}
  efficiency:
    requests_per_second: 11.166666666666666
    cache_hit_rate: 0.0
    queue_depth: 19
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 19.00
- **Baseline Value**: 21.00
- **Deviation**: 2.00 standard deviations
- **Change**: -9.5%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 19
- **Completed Requests (1min)**: 670
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1846.60ms

### Efficiency Metrics

- **Requests/sec**: 11.17
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 19

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 19.0,
    "baseline_value": 21.0,
    "deviation": 2.0,
    "severity": "warning",
    "percentage_change": -9.523809523809524
  },
  "system_state": {
    "active_requests": 19,
    "completed_requests_1min": 670,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1846.597831284822
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.166666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 19
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
