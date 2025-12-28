---
timestamp: 1766924348.186887
datetime: '2025-12-28T07:19:08.186887'
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
  anomaly_id: requests_per_second_1766924348.186887
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.1833333333333333
    baseline_value: 0.9303
    deviation: 4.274756312126479
    severity: warning
    percentage_change: 27.199111397756997
  system_state:
    active_requests: 0
    completed_requests_1min: 71
    error_rate_1min: 0.0
    avg_response_time_1min: 345.4808517241142
  metadata: {}
  efficiency:
    requests_per_second: 1.1833333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.18
- **Baseline Value**: 0.93
- **Deviation**: 4.27 standard deviations
- **Change**: +27.2%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 71
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 345.48ms

### Efficiency Metrics

- **Requests/sec**: 1.18
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.1833333333333333,
    "baseline_value": 0.9303,
    "deviation": 4.274756312126479,
    "severity": "warning",
    "percentage_change": 27.199111397756997
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 71,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 345.4808517241142
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.1833333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
