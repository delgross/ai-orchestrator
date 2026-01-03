---
timestamp: 1767375825.592103
datetime: '2026-01-02T12:43:45.592103'
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
  anomaly_id: requests_per_second_1767375825.592103
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.933333333333334
    baseline_value: 13.3
    deviation: 2.444444444444471
    severity: warning
    percentage_change: -2.7568922305764443
  system_state:
    active_requests: 8
    completed_requests_1min: 776
    error_rate_1min: 0.0
    avg_response_time_1min: 820.8039799301895
  metadata: {}
  efficiency:
    requests_per_second: 12.933333333333334
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.93
- **Baseline Value**: 13.30
- **Deviation**: 2.44 standard deviations
- **Change**: -2.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 776
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 820.80ms

### Efficiency Metrics

- **Requests/sec**: 12.93
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.933333333333334,
    "baseline_value": 13.3,
    "deviation": 2.444444444444471,
    "severity": "warning",
    "percentage_change": -2.7568922305764443
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 776,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 820.8039799301895
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.933333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
