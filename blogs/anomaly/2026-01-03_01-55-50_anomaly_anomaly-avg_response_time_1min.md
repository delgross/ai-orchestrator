---
timestamp: 1767423350.017628
datetime: '2026-01-03T01:55:50.017628'
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
  anomaly_id: avg_response_time_1min_1767423350.017628
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 565.9672170513126
    baseline_value: 473.05284995940684
    deviation: 1.9914186357035428
    severity: warning
    percentage_change: 19.641434799489907
  system_state:
    active_requests: 8
    completed_requests_1min: 818
    error_rate_1min: 0.0
    avg_response_time_1min: 565.9672170513126
  metadata: {}
  efficiency:
    requests_per_second: 13.633333333333333
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 565.97
- **Baseline Value**: 473.05
- **Deviation**: 1.99 standard deviations
- **Change**: +19.6%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 818
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 565.97ms

### Efficiency Metrics

- **Requests/sec**: 13.63
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 565.9672170513126,
    "baseline_value": 473.05284995940684,
    "deviation": 1.9914186357035428,
    "severity": "warning",
    "percentage_change": 19.641434799489907
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 818,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 565.9672170513126
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.633333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
