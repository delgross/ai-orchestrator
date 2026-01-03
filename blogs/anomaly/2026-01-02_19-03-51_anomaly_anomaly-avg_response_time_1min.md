---
timestamp: 1767398631.317377
datetime: '2026-01-02T19:03:51.317377'
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
  anomaly_id: avg_response_time_1min_1767398631.317377
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 427.814052318954
    baseline_value: 432.1166915217722
    deviation: 2.2393658272661736
    severity: warning
    percentage_change: -0.9957123358659794
  system_state:
    active_requests: 6
    completed_requests_1min: 791
    error_rate_1min: 0.0
    avg_response_time_1min: 427.814052318954
  metadata: {}
  efficiency:
    requests_per_second: 13.183333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 427.81
- **Baseline Value**: 432.12
- **Deviation**: 2.24 standard deviations
- **Change**: -1.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 791
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 427.81ms

### Efficiency Metrics

- **Requests/sec**: 13.18
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 427.814052318954,
    "baseline_value": 432.1166915217722,
    "deviation": 2.2393658272661736,
    "severity": "warning",
    "percentage_change": -0.9957123358659794
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 791,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 427.814052318954
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.183333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
