---
timestamp: 1767444328.963417
datetime: '2026-01-03T07:45:28.963417'
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
  anomaly_id: avg_response_time_1min_1767444328.963417
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 470.9848636804625
    baseline_value: 552.904870274455
    deviation: 2.9977482342706043
    severity: warning
    percentage_change: -14.816293181380082
  system_state:
    active_requests: 1
    completed_requests_1min: 258
    error_rate_1min: 0.0
    avg_response_time_1min: 470.9848636804625
  metadata: {}
  efficiency:
    requests_per_second: 4.3
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 470.98
- **Baseline Value**: 552.90
- **Deviation**: 3.00 standard deviations
- **Change**: -14.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 258
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 470.98ms

### Efficiency Metrics

- **Requests/sec**: 4.30
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 470.9848636804625,
    "baseline_value": 552.904870274455,
    "deviation": 2.9977482342706043,
    "severity": "warning",
    "percentage_change": -14.816293181380082
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 258,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 470.9848636804625
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 4.3,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
