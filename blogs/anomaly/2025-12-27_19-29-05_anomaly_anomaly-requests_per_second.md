---
timestamp: 1766881745.232435
datetime: '2025-12-27T19:29:05.232435'
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
  anomaly_id: requests_per_second_1766881745.232435
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 2.5
    baseline_value: 2.4169166666666664
    deviation: 4.604804393869264
    severity: warning
    percentage_change: 3.4375754232320914
  system_state:
    active_requests: 0
    completed_requests_1min: 150
    error_rate_1min: 0.0
    avg_response_time_1min: 174.835155804952
  metadata: {}
  efficiency:
    requests_per_second: 2.5
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 2.50
- **Baseline Value**: 2.42
- **Deviation**: 4.60 standard deviations
- **Change**: +3.4%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 150
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 174.84ms

### Efficiency Metrics

- **Requests/sec**: 2.50
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 2.5,
    "baseline_value": 2.4169166666666664,
    "deviation": 4.604804393869264,
    "severity": "warning",
    "percentage_change": 3.4375754232320914
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 150,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 174.835155804952
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.5,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
