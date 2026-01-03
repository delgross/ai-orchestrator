---
timestamp: 1767405098.660628
datetime: '2026-01-02T20:51:38.660628'
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
  anomaly_id: requests_per_second_1767405098.660628
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.283333333333333
    baseline_value: 6.55
    deviation: 2.111111111111109
    severity: warning
    percentage_change: -19.338422391857506
  system_state:
    active_requests: 6
    completed_requests_1min: 317
    error_rate_1min: 0.0
    avg_response_time_1min: 1069.4117914614994
  metadata: {}
  efficiency:
    requests_per_second: 5.283333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.28
- **Baseline Value**: 6.55
- **Deviation**: 2.11 standard deviations
- **Change**: -19.3%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 317
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1069.41ms

### Efficiency Metrics

- **Requests/sec**: 5.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 5.283333333333333,
    "baseline_value": 6.55,
    "deviation": 2.111111111111109,
    "severity": "warning",
    "percentage_change": -19.338422391857506
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 317,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1069.4117914614994
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.283333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
