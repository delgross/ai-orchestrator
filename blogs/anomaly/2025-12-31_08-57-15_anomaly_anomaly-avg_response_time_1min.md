---
timestamp: 1767189435.3578172
datetime: '2025-12-31T08:57:15.357817'
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
  anomaly_id: avg_response_time_1min_1767189435.3578172
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 120.99072709679604
    baseline_value: 103.58542390167713
    deviation: 1.6510677147245632
    severity: warning
    percentage_change: 16.80284980214972
  system_state:
    active_requests: 0
    completed_requests_1min: 128
    error_rate_1min: 0.0
    avg_response_time_1min: 120.99072709679604
  metadata: {}
  efficiency:
    requests_per_second: 2.1333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 120.99
- **Baseline Value**: 103.59
- **Deviation**: 1.65 standard deviations
- **Change**: +16.8%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 128
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 120.99ms

### Efficiency Metrics

- **Requests/sec**: 2.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 120.99072709679604,
    "baseline_value": 103.58542390167713,
    "deviation": 1.6510677147245632,
    "severity": "warning",
    "percentage_change": 16.80284980214972
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 128,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 120.99072709679604
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.1333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
