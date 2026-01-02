---
timestamp: 1767322609.5670469
datetime: '2026-01-01T21:56:49.567047'
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
  anomaly_id: requests_per_second_1767322609.5670469
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.433333333333334
    baseline_value: 13.033333333333333
    deviation: 1.5000000000000067
    severity: warning
    percentage_change: 3.0690537084399008
  system_state:
    active_requests: 6
    completed_requests_1min: 806
    error_rate_1min: 0.0
    avg_response_time_1min: 446.5278079432826
  metadata: {}
  efficiency:
    requests_per_second: 13.433333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.43
- **Baseline Value**: 13.03
- **Deviation**: 1.50 standard deviations
- **Change**: +3.1%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 806
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 446.53ms

### Efficiency Metrics

- **Requests/sec**: 13.43
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.433333333333334,
    "baseline_value": 13.033333333333333,
    "deviation": 1.5000000000000067,
    "severity": "warning",
    "percentage_change": 3.0690537084399008
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 806,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 446.5278079432826
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.433333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
