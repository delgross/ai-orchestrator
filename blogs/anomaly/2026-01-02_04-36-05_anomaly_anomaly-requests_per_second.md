---
timestamp: 1767346565.635616
datetime: '2026-01-02T04:36:05.635616'
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
  anomaly_id: requests_per_second_1767346565.635616
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 14.05
    baseline_value: 13.9
    deviation: 1.5000000000000089
    severity: warning
    percentage_change: 1.0791366906474844
  system_state:
    active_requests: 6
    completed_requests_1min: 843
    error_rate_1min: 0.0
    avg_response_time_1min: 431.4466594659844
  metadata: {}
  efficiency:
    requests_per_second: 14.05
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 14.05
- **Baseline Value**: 13.90
- **Deviation**: 1.50 standard deviations
- **Change**: +1.1%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 843
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 431.45ms

### Efficiency Metrics

- **Requests/sec**: 14.05
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 14.05,
    "baseline_value": 13.9,
    "deviation": 1.5000000000000089,
    "severity": "warning",
    "percentage_change": 1.0791366906474844
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 843,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 431.4466594659844
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.05,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
