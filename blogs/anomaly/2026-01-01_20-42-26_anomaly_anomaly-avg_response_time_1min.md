---
timestamp: 1767318146.131799
datetime: '2026-01-01T20:42:26.131799'
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
  anomaly_id: avg_response_time_1min_1767318146.131799
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 116.38610423793199
    baseline_value: 178.12463215419226
    deviation: 1.5136218651496196
    severity: warning
    percentage_change: -34.66029777555794
  system_state:
    active_requests: 2
    completed_requests_1min: 353
    error_rate_1min: 0.0
    avg_response_time_1min: 116.38610423793199
  metadata: {}
  efficiency:
    requests_per_second: 5.883333333333334
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 116.39
- **Baseline Value**: 178.12
- **Deviation**: 1.51 standard deviations
- **Change**: -34.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 353
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 116.39ms

### Efficiency Metrics

- **Requests/sec**: 5.88
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 116.38610423793199,
    "baseline_value": 178.12463215419226,
    "deviation": 1.5136218651496196,
    "severity": "warning",
    "percentage_change": -34.66029777555794
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 353,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 116.38610423793199
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.883333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
