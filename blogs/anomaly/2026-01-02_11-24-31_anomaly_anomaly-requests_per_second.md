---
timestamp: 1767371071.564375
datetime: '2026-01-02T11:24:31.564375'
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
  anomaly_id: requests_per_second_1767371071.564375
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.433333333333334
    baseline_value: 12.733333333333333
    deviation: 1.9999999999999882
    severity: warning
    percentage_change: -2.3560209424083687
  system_state:
    active_requests: 9
    completed_requests_1min: 746
    error_rate_1min: 0.0
    avg_response_time_1min: 1047.7416959588713
  metadata: {}
  efficiency:
    requests_per_second: 12.433333333333334
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.43
- **Baseline Value**: 12.73
- **Deviation**: 2.00 standard deviations
- **Change**: -2.4%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 746
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1047.74ms

### Efficiency Metrics

- **Requests/sec**: 12.43
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.433333333333334,
    "baseline_value": 12.733333333333333,
    "deviation": 1.9999999999999882,
    "severity": "warning",
    "percentage_change": -2.3560209424083687
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 746,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1047.7416959588713
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.433333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
