---
timestamp: 1767441208.338669
datetime: '2026-01-03T06:53:28.338669'
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
  anomaly_id: requests_per_second_1767441208.338669
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.4
    baseline_value: 11.533333333333333
    deviation: 2.0
    severity: warning
    percentage_change: -1.1560693641618456
  system_state:
    active_requests: 6
    completed_requests_1min: 684
    error_rate_1min: 0.0
    avg_response_time_1min: 534.3797551958185
  metadata: {}
  efficiency:
    requests_per_second: 11.4
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.40
- **Baseline Value**: 11.53
- **Deviation**: 2.00 standard deviations
- **Change**: -1.2%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 684
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 534.38ms

### Efficiency Metrics

- **Requests/sec**: 11.40
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.4,
    "baseline_value": 11.533333333333333,
    "deviation": 2.0,
    "severity": "warning",
    "percentage_change": -1.1560693641618456
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 684,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 534.3797551958185
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.4,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
