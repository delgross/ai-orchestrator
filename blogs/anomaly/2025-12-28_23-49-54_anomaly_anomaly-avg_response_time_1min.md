---
timestamp: 1766983794.4202938
datetime: '2025-12-28T23:49:54.420294'
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
  anomaly_id: avg_response_time_1min_1766983794.4202938
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 211.9192572740408
    baseline_value: 151.9662171547664
    deviation: 4.294960283116213
    severity: warning
    percentage_change: 39.45155788027324
  system_state:
    active_requests: 1
    completed_requests_1min: 104
    error_rate_1min: 0.0
    avg_response_time_1min: 211.9192572740408
  metadata: {}
  efficiency:
    requests_per_second: 1.7333333333333334
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 211.92
- **Baseline Value**: 151.97
- **Deviation**: 4.29 standard deviations
- **Change**: +39.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 104
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 211.92ms

### Efficiency Metrics

- **Requests/sec**: 1.73
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 211.9192572740408,
    "baseline_value": 151.9662171547664,
    "deviation": 4.294960283116213,
    "severity": "warning",
    "percentage_change": 39.45155788027324
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 104,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 211.9192572740408
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.7333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
