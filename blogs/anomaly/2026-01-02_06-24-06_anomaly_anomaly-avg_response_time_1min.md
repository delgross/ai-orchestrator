---
timestamp: 1767353046.697856
datetime: '2026-01-02T06:24:06.697856'
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
  anomaly_id: avg_response_time_1min_1767353046.697856
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 496.0140499472618
    baseline_value: 460.08265090536463
    deviation: 2.944706890985848
    severity: warning
    percentage_change: 7.809770477367552
  system_state:
    active_requests: 7
    completed_requests_1min: 800
    error_rate_1min: 0.0
    avg_response_time_1min: 496.0140499472618
  metadata: {}
  efficiency:
    requests_per_second: 13.333333333333334
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 496.01
- **Baseline Value**: 460.08
- **Deviation**: 2.94 standard deviations
- **Change**: +7.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 800
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 496.01ms

### Efficiency Metrics

- **Requests/sec**: 13.33
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 496.0140499472618,
    "baseline_value": 460.08265090536463,
    "deviation": 2.944706890985848,
    "severity": "warning",
    "percentage_change": 7.809770477367552
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 800,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 496.0140499472618
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
