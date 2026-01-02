---
timestamp: 1767321769.367184
datetime: '2026-01-01T21:42:49.367184'
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
  anomaly_id: avg_response_time_1min_1767321769.367184
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 445.0908716814018
    baseline_value: 460.6282604046357
    deviation: 1.5704317335591464
    severity: warning
    percentage_change: -3.373086295136384
  system_state:
    active_requests: 6
    completed_requests_1min: 810
    error_rate_1min: 0.0
    avg_response_time_1min: 445.0908716814018
  metadata: {}
  efficiency:
    requests_per_second: 13.5
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 445.09
- **Baseline Value**: 460.63
- **Deviation**: 1.57 standard deviations
- **Change**: -3.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 810
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 445.09ms

### Efficiency Metrics

- **Requests/sec**: 13.50
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 445.0908716814018,
    "baseline_value": 460.6282604046357,
    "deviation": 1.5704317335591464,
    "severity": "warning",
    "percentage_change": -3.373086295136384
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 810,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 445.0908716814018
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.5,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
