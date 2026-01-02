---
timestamp: 1767318613.533576
datetime: '2026-01-01T20:50:13.533576'
category: anomaly
severity: warning
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: requests_per_second_1767318613.533576
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.8
    baseline_value: 2.2
    deviation: 2.0377358490566033
    severity: warning
    percentage_change: 163.6363636363636
  system_state:
    active_requests: 1
    completed_requests_1min: 348
    error_rate_1min: 0.0
    avg_response_time_1min: 108.61422070141496
  metadata: {}
  efficiency:
    requests_per_second: 5.8
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.80
- **Baseline Value**: 2.20
- **Deviation**: 2.04 standard deviations
- **Change**: +163.6%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 348
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 108.61ms

### Efficiency Metrics

- **Requests/sec**: 5.80
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 5.8,
    "baseline_value": 2.2,
    "deviation": 2.0377358490566033,
    "severity": "warning",
    "percentage_change": 163.6363636363636
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 348,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 108.61422070141496
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.8,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
