---
timestamp: 1767370051.326463
datetime: '2026-01-02T11:07:31.326463'
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
  anomaly_id: requests_per_second_1767370051.326463
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.133333333333333
    baseline_value: 8.433333333333334
    deviation: 2.740740740740739
    severity: warning
    percentage_change: 43.87351778656126
  system_state:
    active_requests: 10
    completed_requests_1min: 728
    error_rate_1min: 0.0
    avg_response_time_1min: 1059.0674028946803
  metadata: {}
  efficiency:
    requests_per_second: 12.133333333333333
    cache_hit_rate: 0.0
    queue_depth: 10
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.13
- **Baseline Value**: 8.43
- **Deviation**: 2.74 standard deviations
- **Change**: +43.9%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 10
- **Completed Requests (1min)**: 728
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1059.07ms

### Efficiency Metrics

- **Requests/sec**: 12.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 10

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.133333333333333,
    "baseline_value": 8.433333333333334,
    "deviation": 2.740740740740739,
    "severity": "warning",
    "percentage_change": 43.87351778656126
  },
  "system_state": {
    "active_requests": 10,
    "completed_requests_1min": 728,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1059.0674028946803
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.133333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 10
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
