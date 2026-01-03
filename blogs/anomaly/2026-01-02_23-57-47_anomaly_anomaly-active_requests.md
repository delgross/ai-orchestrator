---
timestamp: 1767416267.464288
datetime: '2026-01-02T23:57:47.464288'
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
  anomaly_id: active_requests_1767416267.464288
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 28.0
    baseline_value: 10.0
    deviation: 1.8
    severity: warning
    percentage_change: 180.0
  system_state:
    active_requests: 28
    completed_requests_1min: 1465
    error_rate_1min: 0.0
    avg_response_time_1min: 1027.290043326368
  metadata: {}
  efficiency:
    requests_per_second: 24.416666666666668
    cache_hit_rate: 0.0
    queue_depth: 28
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 28.00
- **Baseline Value**: 10.00
- **Deviation**: 1.80 standard deviations
- **Change**: +180.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 28
- **Completed Requests (1min)**: 1465
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1027.29ms

### Efficiency Metrics

- **Requests/sec**: 24.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 28

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 28.0,
    "baseline_value": 10.0,
    "deviation": 1.8,
    "severity": "warning",
    "percentage_change": 180.0
  },
  "system_state": {
    "active_requests": 28,
    "completed_requests_1min": 1465,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1027.290043326368
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 24.416666666666668,
    "cache_hit_rate": 0.0,
    "queue_depth": 28
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
