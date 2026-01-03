---
timestamp: 1767461376.1920881
datetime: '2026-01-03T12:29:36.192088'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: avg_response_time_1min_1767461376.1920881
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1219.2492485046387
    baseline_value: 650.7686528583502
    deviation: 1.760916270403832
    severity: warning
    percentage_change: 87.35525184708415
  system_state:
    active_requests: 0
    completed_requests_1min: 4
    error_rate_1min: 0.0
    avg_response_time_1min: 1219.2492485046387
  metadata: {}
  efficiency:
    requests_per_second: 0.06666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1219.25
- **Baseline Value**: 650.77
- **Deviation**: 1.76 standard deviations
- **Change**: +87.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 4
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1219.25ms

### Efficiency Metrics

- **Requests/sec**: 0.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1219.2492485046387,
    "baseline_value": 650.7686528583502,
    "deviation": 1.760916270403832,
    "severity": "warning",
    "percentage_change": 87.35525184708415
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 4,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1219.2492485046387
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.06666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
