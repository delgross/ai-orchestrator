---
timestamp: 1767422989.960141
datetime: '2026-01-03T01:49:49.960141'
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
  anomaly_id: requests_per_second_1767422989.960141
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 14.133333333333333
    baseline_value: 14.033333333333333
    deviation: 1.9999999999999645
    severity: warning
    percentage_change: 0.7125890736342018
  system_state:
    active_requests: 8
    completed_requests_1min: 848
    error_rate_1min: 0.0
    avg_response_time_1min: 507.0989368096837
  metadata: {}
  efficiency:
    requests_per_second: 14.133333333333333
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 14.13
- **Baseline Value**: 14.03
- **Deviation**: 2.00 standard deviations
- **Change**: +0.7%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 848
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 507.10ms

### Efficiency Metrics

- **Requests/sec**: 14.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 14.133333333333333,
    "baseline_value": 14.033333333333333,
    "deviation": 1.9999999999999645,
    "severity": "warning",
    "percentage_change": 0.7125890736342018
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 848,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 507.0989368096837
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.133333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
