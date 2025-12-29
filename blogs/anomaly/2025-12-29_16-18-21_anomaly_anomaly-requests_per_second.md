---
timestamp: 1767043101.786983
datetime: '2025-12-29T16:18:21.786983'
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
  anomaly_id: requests_per_second_1767043101.786983
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.25
    baseline_value: 0.027556237218813905
    deviation: 4.963171861979238
    severity: warning
    percentage_change: 807.2356215213359
  system_state:
    active_requests: 1
    completed_requests_1min: 15
    error_rate_1min: 0.0
    avg_response_time_1min: 4150.848929087321
  metadata: {}
  efficiency:
    requests_per_second: 0.25
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.25
- **Baseline Value**: 0.03
- **Deviation**: 4.96 standard deviations
- **Change**: +807.2%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 15
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 4150.85ms

### Efficiency Metrics

- **Requests/sec**: 0.25
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 0.25,
    "baseline_value": 0.027556237218813905,
    "deviation": 4.963171861979238,
    "severity": "warning",
    "percentage_change": 807.2356215213359
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 15,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 4150.848929087321
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.25,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
