---
timestamp: 1767022711.318857
datetime: '2025-12-29T10:38:31.318857'
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
  anomaly_id: active_requests_1767022711.318857
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 1.0
    baseline_value: 0.03571428571428571
    deviation: 5.172903301959991
    severity: warning
    percentage_change: 2700.0000000000005
  system_state:
    active_requests: 1
    completed_requests_1min: 226
    error_rate_1min: 0.0
    avg_response_time_1min: 370.44316582975136
  metadata: {}
  efficiency:
    requests_per_second: 3.7666666666666666
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
- **Deviation**: 5.17 standard deviations
- **Change**: +2700.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 226
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 370.44ms

### Efficiency Metrics

- **Requests/sec**: 3.77
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 1.0,
    "baseline_value": 0.03571428571428571,
    "deviation": 5.172903301959991,
    "severity": "warning",
    "percentage_change": 2700.0000000000005
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 226,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 370.44316582975136
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.7666666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
