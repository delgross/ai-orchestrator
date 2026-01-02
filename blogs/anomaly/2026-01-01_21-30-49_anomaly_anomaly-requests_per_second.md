---
timestamp: 1767321049.249537
datetime: '2026-01-01T21:30:49.249537'
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
  anomaly_id: requests_per_second_1767321049.249537
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.766666666666667
    baseline_value: 13.083333333333334
    deviation: 1.5833333333333377
    severity: warning
    percentage_change: -2.4203821656050937
  system_state:
    active_requests: 6
    completed_requests_1min: 766
    error_rate_1min: 0.0
    avg_response_time_1min: 466.9557819167254
  metadata: {}
  efficiency:
    requests_per_second: 12.766666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.77
- **Baseline Value**: 13.08
- **Deviation**: 1.58 standard deviations
- **Change**: -2.4%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 766
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 466.96ms

### Efficiency Metrics

- **Requests/sec**: 12.77
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.766666666666667,
    "baseline_value": 13.083333333333334,
    "deviation": 1.5833333333333377,
    "severity": "warning",
    "percentage_change": -2.4203821656050937
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 766,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 466.9557819167254
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.766666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
