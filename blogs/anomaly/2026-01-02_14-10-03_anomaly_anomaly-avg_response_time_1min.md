---
timestamp: 1767381003.738074
datetime: '2026-01-02T14:10:03.738074'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: avg_response_time_1min_1767381003.738074
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 505.27837268122425
    baseline_value: 395.8457793718503
    deviation: 2.1560891994716376
    severity: warning
    percentage_change: 27.64525959655994
  system_state:
    active_requests: 9
    completed_requests_1min: 1144
    error_rate_1min: 0.0
    avg_response_time_1min: 505.27837268122425
  metadata: {}
  efficiency:
    requests_per_second: 19.066666666666666
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 505.28
- **Baseline Value**: 395.85
- **Deviation**: 2.16 standard deviations
- **Change**: +27.6%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 1144
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 505.28ms

### Efficiency Metrics

- **Requests/sec**: 19.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 505.27837268122425,
    "baseline_value": 395.8457793718503,
    "deviation": 2.1560891994716376,
    "severity": "warning",
    "percentage_change": 27.64525959655994
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 1144,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 505.27837268122425
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 19.066666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
