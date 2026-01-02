---
timestamp: 1767370771.485837
datetime: '2026-01-02T11:19:31.485837'
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
  anomaly_id: requests_per_second_1767370771.485837
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.283333333333333
    baseline_value: 11.8
    deviation: 2.0714285714285596
    severity: warning
    percentage_change: 4.096045197740105
  system_state:
    active_requests: 14
    completed_requests_1min: 737
    error_rate_1min: 0.0
    avg_response_time_1min: 1087.6755688536605
  metadata: {}
  efficiency:
    requests_per_second: 12.283333333333333
    cache_hit_rate: 0.0
    queue_depth: 14
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.28
- **Baseline Value**: 11.80
- **Deviation**: 2.07 standard deviations
- **Change**: +4.1%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 14
- **Completed Requests (1min)**: 737
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1087.68ms

### Efficiency Metrics

- **Requests/sec**: 12.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 14

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.283333333333333,
    "baseline_value": 11.8,
    "deviation": 2.0714285714285596,
    "severity": "warning",
    "percentage_change": 4.096045197740105
  },
  "system_state": {
    "active_requests": 14,
    "completed_requests_1min": 737,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1087.6755688536605
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.283333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 14
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
