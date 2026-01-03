---
timestamp: 1767415066.779319
datetime: '2026-01-02T23:37:46.779319'
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
  anomaly_id: active_requests_1767415066.779319
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 27.0
    baseline_value: 10.0
    deviation: 1.7
    severity: warning
    percentage_change: 170.0
  system_state:
    active_requests: 27
    completed_requests_1min: 551
    error_rate_1min: 0.0
    avg_response_time_1min: 2914.834517532598
  metadata: {}
  efficiency:
    requests_per_second: 9.183333333333334
    cache_hit_rate: 0.0
    queue_depth: 27
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 27.00
- **Baseline Value**: 10.00
- **Deviation**: 1.70 standard deviations
- **Change**: +170.0%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 27
- **Completed Requests (1min)**: 551
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2914.83ms

### Efficiency Metrics

- **Requests/sec**: 9.18
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 27

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 27.0,
    "baseline_value": 10.0,
    "deviation": 1.7,
    "severity": "warning",
    "percentage_change": 170.0
  },
  "system_state": {
    "active_requests": 27,
    "completed_requests_1min": 551,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2914.834517532598
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 9.183333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 27
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
