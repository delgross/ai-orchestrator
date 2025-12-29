---
timestamp: 1766982174.294899
datetime: '2025-12-28T23:22:54.294899'
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
  anomaly_id: active_requests_1766982174.294899
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 0.0
    baseline_value: 1.011
    deviation: 5.410680469590877
    severity: warning
    percentage_change: -100.0
  system_state:
    active_requests: 0
    completed_requests_1min: 95
    error_rate_1min: 0.0
    avg_response_time_1min: 156.21410922000283
  metadata: {}
  efficiency:
    requests_per_second: 1.5833333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 0.00
- **Baseline Value**: 1.01
- **Deviation**: 5.41 standard deviations
- **Change**: -100.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 95
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 156.21ms

### Efficiency Metrics

- **Requests/sec**: 1.58
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 0.0,
    "baseline_value": 1.011,
    "deviation": 5.410680469590877,
    "severity": "warning",
    "percentage_change": -100.0
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 95,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 156.21410922000283
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.5833333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
