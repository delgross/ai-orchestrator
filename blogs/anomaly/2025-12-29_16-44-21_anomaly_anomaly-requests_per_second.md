---
timestamp: 1767044661.8589718
datetime: '2025-12-29T16:44:21.858972'
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
  anomaly_id: requests_per_second_1767044661.8589718
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.65
    baseline_value: 0.07670454545454546
    deviation: 5.571187921202185
    severity: warning
    percentage_change: 2051.111111111111
  system_state:
    active_requests: 0
    completed_requests_1min: 99
    error_rate_1min: 0.0
    avg_response_time_1min: 118.16254529086027
  metadata: {}
  efficiency:
    requests_per_second: 1.65
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.65
- **Baseline Value**: 0.08
- **Deviation**: 5.57 standard deviations
- **Change**: +2051.1%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 99
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 118.16ms

### Efficiency Metrics

- **Requests/sec**: 1.65
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.65,
    "baseline_value": 0.07670454545454546,
    "deviation": 5.571187921202185,
    "severity": "warning",
    "percentage_change": 2051.111111111111
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 99,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 118.16254529086027
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.65,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
