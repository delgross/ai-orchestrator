---
timestamp: 1767398931.4301
datetime: '2026-01-02T19:08:51.430100'
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
  anomaly_id: requests_per_second_1767398931.4301
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.75
    baseline_value: 13.933333333333334
    deviation: 1.8333333333333421
    severity: warning
    percentage_change: -1.3157894736842122
  system_state:
    active_requests: 6
    completed_requests_1min: 825
    error_rate_1min: 0.0
    avg_response_time_1min: 432.5147146167177
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
- **Baseline Value**: 13.93
- **Deviation**: 1.83 standard deviations
- **Change**: -1.3%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 825
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 432.51ms

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
    "baseline_value": 13.933333333333334,
    "deviation": 1.8333333333333421,
    "severity": "warning",
    "percentage_change": -1.3157894736842122
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 825,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 432.5147146167177
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
