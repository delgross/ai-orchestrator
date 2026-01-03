---
timestamp: 1767436407.267057
datetime: '2026-01-03T05:33:27.267057'
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
  anomaly_id: requests_per_second_1767436407.267057
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.683333333333334
    baseline_value: 11.533333333333333
    deviation: 1.5000000000000089
    severity: warning
    percentage_change: 1.300578034682084
  system_state:
    active_requests: 6
    completed_requests_1min: 701
    error_rate_1min: 0.0
    avg_response_time_1min: 513.7946231559067
  metadata: {}
  efficiency:
    requests_per_second: 11.683333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.68
- **Baseline Value**: 11.53
- **Deviation**: 1.50 standard deviations
- **Change**: +1.3%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 701
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 513.79ms

### Efficiency Metrics

- **Requests/sec**: 11.68
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.683333333333334,
    "baseline_value": 11.533333333333333,
    "deviation": 1.5000000000000089,
    "severity": "warning",
    "percentage_change": 1.300578034682084
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 701,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 513.7946231559067
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.683333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
