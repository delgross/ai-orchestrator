---
timestamp: 1766866744.25195
datetime: '2025-12-27T15:19:04.251950'
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
  anomaly_id: requests_per_second_1766866744.25195
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.8833333333333333
    baseline_value: 2.3430166666666663
    deviation: 4.46079062755544
    severity: warning
    percentage_change: -62.29931498566662
  system_state:
    active_requests: 0
    completed_requests_1min: 53
    error_rate_1min: 0.0
    avg_response_time_1min: 8.328217380451706
  metadata: {}
  efficiency:
    requests_per_second: 0.8833333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.88
- **Baseline Value**: 2.34
- **Deviation**: 4.46 standard deviations
- **Change**: -62.3%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 53
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 8.33ms

### Efficiency Metrics

- **Requests/sec**: 0.88
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 0.8833333333333333,
    "baseline_value": 2.3430166666666663,
    "deviation": 4.46079062755544,
    "severity": "warning",
    "percentage_change": -62.29931498566662
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 53,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 8.328217380451706
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.8833333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
