---
timestamp: 1767353406.7464068
datetime: '2026-01-02T06:30:06.746407'
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
  anomaly_id: avg_response_time_1min_1767353406.7464068
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 495.43992668427387
    baseline_value: 465.67500878765856
    deviation: 1.6918155679352638
    severity: warning
    percentage_change: 6.39177910236272
  system_state:
    active_requests: 7
    completed_requests_1min: 803
    error_rate_1min: 0.0
    avg_response_time_1min: 495.43992668427387
  metadata: {}
  efficiency:
    requests_per_second: 13.383333333333333
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 495.44
- **Baseline Value**: 465.68
- **Deviation**: 1.69 standard deviations
- **Change**: +6.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 803
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 495.44ms

### Efficiency Metrics

- **Requests/sec**: 13.38
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 495.43992668427387,
    "baseline_value": 465.67500878765856,
    "deviation": 1.6918155679352638,
    "severity": "warning",
    "percentage_change": 6.39177910236272
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 803,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 495.43992668427387
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.383333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
