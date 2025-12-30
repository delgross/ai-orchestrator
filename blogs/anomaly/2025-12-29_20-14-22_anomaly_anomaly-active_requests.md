---
timestamp: 1767057262.706757
datetime: '2025-12-29T20:14:22.706757'
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
  anomaly_id: active_requests_1767057262.706757
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 7.0
    baseline_value: 0.606
    deviation: 5.054325367524465
    severity: warning
    percentage_change: 1055.1155115511551
  system_state:
    active_requests: 7
    completed_requests_1min: 134
    error_rate_1min: 0.0
    avg_response_time_1min: 1349.851747057331
  metadata: {}
  efficiency:
    requests_per_second: 2.2333333333333334
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 7.00
- **Baseline Value**: 0.61
- **Deviation**: 5.05 standard deviations
- **Change**: +1055.1%
- **Severity**: WARNING

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 134
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1349.85ms

### Efficiency Metrics

- **Requests/sec**: 2.23
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 7.0,
    "baseline_value": 0.606,
    "deviation": 5.054325367524465,
    "severity": "warning",
    "percentage_change": 1055.1155115511551
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 134,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1349.851747057331
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.2333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
