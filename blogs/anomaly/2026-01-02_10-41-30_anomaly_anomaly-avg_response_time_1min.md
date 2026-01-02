---
timestamp: 1767368490.882051
datetime: '2026-01-02T10:41:30.882051'
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
  anomaly_id: avg_response_time_1min_1767368490.882051
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 3356.9817983803628
    baseline_value: 2021.4287755009648
    deviation: 2.015058153713787
    severity: warning
    percentage_change: 66.0697541791158
  system_state:
    active_requests: 13
    completed_requests_1min: 238
    error_rate_1min: 0.0
    avg_response_time_1min: 3356.9817983803628
  metadata: {}
  efficiency:
    requests_per_second: 3.966666666666667
    cache_hit_rate: 0.0
    queue_depth: 13
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 3356.98
- **Baseline Value**: 2021.43
- **Deviation**: 2.02 standard deviations
- **Change**: +66.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 13
- **Completed Requests (1min)**: 238
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 3356.98ms

### Efficiency Metrics

- **Requests/sec**: 3.97
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 13

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 3356.9817983803628,
    "baseline_value": 2021.4287755009648,
    "deviation": 2.015058153713787,
    "severity": "warning",
    "percentage_change": 66.0697541791158
  },
  "system_state": {
    "active_requests": 13,
    "completed_requests_1min": 238,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 3356.9817983803628
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.966666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 13
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
