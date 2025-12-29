---
timestamp: 1767041361.684969
datetime: '2025-12-29T15:49:21.684969'
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
  anomaly_id: active_requests_1767041361.684969
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 4.0
    baseline_value: 0.11447811447811448
    deviation: 5.911177718648629
    severity: warning
    percentage_change: 3394.1176470588234
  system_state:
    active_requests: 4
    completed_requests_1min: 6
    error_rate_1min: 0.0
    avg_response_time_1min: 39662.541230519615
  metadata: {}
  efficiency:
    requests_per_second: 0.1
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 4.00
- **Baseline Value**: 0.11
- **Deviation**: 5.91 standard deviations
- **Change**: +3394.1%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 6
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 39662.54ms

### Efficiency Metrics

- **Requests/sec**: 0.10
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 4.0,
    "baseline_value": 0.11447811447811448,
    "deviation": 5.911177718648629,
    "severity": "warning",
    "percentage_change": 3394.1176470588234
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 6,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 39662.541230519615
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.1,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
