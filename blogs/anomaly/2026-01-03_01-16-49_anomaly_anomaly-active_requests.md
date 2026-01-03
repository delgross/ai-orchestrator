---
timestamp: 1767421009.4180229
datetime: '2026-01-03T01:16:49.418023'
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
  anomaly_id: active_requests_1767421009.4180229
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 21.0
    baseline_value: 18.0
    deviation: 1.5
    severity: warning
    percentage_change: 16.666666666666664
  system_state:
    active_requests: 21
    completed_requests_1min: 2440
    error_rate_1min: 0.0
    avg_response_time_1min: 413.72359522053455
  metadata: {}
  efficiency:
    requests_per_second: 40.666666666666664
    cache_hit_rate: 0.0
    queue_depth: 21
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 21.00
- **Baseline Value**: 18.00
- **Deviation**: 1.50 standard deviations
- **Change**: +16.7%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 21
- **Completed Requests (1min)**: 2440
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 413.72ms

### Efficiency Metrics

- **Requests/sec**: 40.67
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 21

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 21.0,
    "baseline_value": 18.0,
    "deviation": 1.5,
    "severity": "warning",
    "percentage_change": 16.666666666666664
  },
  "system_state": {
    "active_requests": 21,
    "completed_requests_1min": 2440,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 413.72359522053455
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 40.666666666666664,
    "cache_hit_rate": 0.0,
    "queue_depth": 21
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
