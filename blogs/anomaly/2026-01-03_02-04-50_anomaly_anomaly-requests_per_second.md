---
timestamp: 1767423890.230914
datetime: '2026-01-03T02:04:50.230914'
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
  anomaly_id: requests_per_second_1767423890.230914
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.816666666666666
    baseline_value: 13.95
    deviation: 1.9999999999999467
    severity: warning
    percentage_change: -0.9557945041815976
  system_state:
    active_requests: 6
    completed_requests_1min: 829
    error_rate_1min: 0.0
    avg_response_time_1min: 432.38917190864663
  metadata: {}
  efficiency:
    requests_per_second: 13.816666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.82
- **Baseline Value**: 13.95
- **Deviation**: 2.00 standard deviations
- **Change**: -1.0%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 829
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 432.39ms

### Efficiency Metrics

- **Requests/sec**: 13.82
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.816666666666666,
    "baseline_value": 13.95,
    "deviation": 1.9999999999999467,
    "severity": "warning",
    "percentage_change": -0.9557945041815976
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 829,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 432.38917190864663
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.816666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
