---
timestamp: 1767259487.4535968
datetime: '2026-01-01T04:24:47.453597'
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
  anomaly_id: avg_response_time_1min_1767259487.4535968
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1079.7817119653673
    baseline_value: 550.337901191106
    deviation: 1.814815028988257
    severity: warning
    percentage_change: 96.2034069665885
  system_state:
    active_requests: 1
    completed_requests_1min: 69
    error_rate_1min: 0.0
    avg_response_time_1min: 1079.7817119653673
  metadata: {}
  efficiency:
    requests_per_second: 1.15
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1079.78
- **Baseline Value**: 550.34
- **Deviation**: 1.81 standard deviations
- **Change**: +96.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 69
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1079.78ms

### Efficiency Metrics

- **Requests/sec**: 1.15
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1079.7817119653673,
    "baseline_value": 550.337901191106,
    "deviation": 1.814815028988257,
    "severity": "warning",
    "percentage_change": 96.2034069665885
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 69,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1079.7817119653673
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.15,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
