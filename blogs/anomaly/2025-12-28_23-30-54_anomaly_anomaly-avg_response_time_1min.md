---
timestamp: 1766982654.3311949
datetime: '2025-12-28T23:30:54.331195'
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
  anomaly_id: avg_response_time_1min_1766982654.3311949
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 208.10969911440455
    baseline_value: 151.6897654017448
    deviation: 4.140728058338565
    severity: warning
    percentage_change: 37.194291627542306
  system_state:
    active_requests: 1
    completed_requests_1min: 99
    error_rate_1min: 0.0
    avg_response_time_1min: 208.10969911440455
  metadata: {}
  efficiency:
    requests_per_second: 1.65
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 208.11
- **Baseline Value**: 151.69
- **Deviation**: 4.14 standard deviations
- **Change**: +37.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 99
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 208.11ms

### Efficiency Metrics

- **Requests/sec**: 1.65
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 208.10969911440455,
    "baseline_value": 151.6897654017448,
    "deviation": 4.140728058338565,
    "severity": "warning",
    "percentage_change": 37.194291627542306
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 99,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 208.10969911440455
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.65,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
