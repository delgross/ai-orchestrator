---
timestamp: 1767322309.466315
datetime: '2026-01-01T21:51:49.466315'
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
  anomaly_id: requests_per_second_1767322309.466315
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.216666666666667
    baseline_value: 13.316666666666666
    deviation: 1.5
    severity: warning
    percentage_change: -0.7509386733416745
  system_state:
    active_requests: 6
    completed_requests_1min: 793
    error_rate_1min: 0.0
    avg_response_time_1min: 451.14583115259006
  metadata: {}
  efficiency:
    requests_per_second: 13.216666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.22
- **Baseline Value**: 13.32
- **Deviation**: 1.50 standard deviations
- **Change**: -0.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 793
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 451.15ms

### Efficiency Metrics

- **Requests/sec**: 13.22
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.216666666666667,
    "baseline_value": 13.316666666666666,
    "deviation": 1.5,
    "severity": "warning",
    "percentage_change": -0.7509386733416745
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 793,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 451.14583115259006
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.216666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
