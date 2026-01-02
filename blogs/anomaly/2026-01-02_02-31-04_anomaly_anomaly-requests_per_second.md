---
timestamp: 1767339064.5754938
datetime: '2026-01-02T02:31:04.575494'
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
  anomaly_id: requests_per_second_1767339064.5754938
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.75
    baseline_value: 13.966666666666667
    deviation: 1.8571428571428505
    severity: warning
    percentage_change: -1.5513126491646787
  system_state:
    active_requests: 6
    completed_requests_1min: 825
    error_rate_1min: 0.0
    avg_response_time_1min: 440.9039136135217
  metadata: {}
  efficiency:
    requests_per_second: 13.75
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.75
- **Baseline Value**: 13.97
- **Deviation**: 1.86 standard deviations
- **Change**: -1.6%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 825
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 440.90ms

### Efficiency Metrics

- **Requests/sec**: 13.75
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.75,
    "baseline_value": 13.966666666666667,
    "deviation": 1.8571428571428505,
    "severity": "warning",
    "percentage_change": -1.5513126491646787
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 825,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 440.9039136135217
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.75,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
