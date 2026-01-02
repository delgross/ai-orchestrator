---
timestamp: 1767346265.584399
datetime: '2026-01-02T04:31:05.584399'
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
  anomaly_id: requests_per_second_1767346265.584399
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.766666666666667
    baseline_value: 13.916666666666666
    deviation: 1.79999999999997
    severity: warning
    percentage_change: -1.0778443113772354
  system_state:
    active_requests: 6
    completed_requests_1min: 826
    error_rate_1min: 0.0
    avg_response_time_1min: 442.0386945364262
  metadata: {}
  efficiency:
    requests_per_second: 13.766666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.77
- **Baseline Value**: 13.92
- **Deviation**: 1.80 standard deviations
- **Change**: -1.1%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 826
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 442.04ms

### Efficiency Metrics

- **Requests/sec**: 13.77
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.766666666666667,
    "baseline_value": 13.916666666666666,
    "deviation": 1.79999999999997,
    "severity": "warning",
    "percentage_change": -1.0778443113772354
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 826,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 442.0386945364262
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.766666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
