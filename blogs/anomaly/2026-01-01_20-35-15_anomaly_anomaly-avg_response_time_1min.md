---
timestamp: 1767317715.095977
datetime: '2026-01-01T20:35:15.095977'
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
  anomaly_id: avg_response_time_1min_1767317715.095977
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 322.7347224366431
    baseline_value: 193.03278337445175
    deviation: 2.6699562088057784
    severity: warning
    percentage_change: 67.19166392093668
  system_state:
    active_requests: 0
    completed_requests_1min: 255
    error_rate_1min: 0.0
    avg_response_time_1min: 322.7347224366431
  metadata: {}
  efficiency:
    requests_per_second: 4.25
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 322.73
- **Baseline Value**: 193.03
- **Deviation**: 2.67 standard deviations
- **Change**: +67.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 255
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 322.73ms

### Efficiency Metrics

- **Requests/sec**: 4.25
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 322.7347224366431,
    "baseline_value": 193.03278337445175,
    "deviation": 2.6699562088057784,
    "severity": "warning",
    "percentage_change": 67.19166392093668
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 255,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 322.7347224366431
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 4.25,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
