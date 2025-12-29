---
timestamp: 1767044961.8748071
datetime: '2025-12-29T16:49:21.874807'
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
  anomaly_id: requests_per_second_1767044961.8748071
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.6
    baseline_value: 0.09873949579831932
    deviation: 4.468619666552001
    severity: warning
    percentage_change: 1520.4255319148936
  system_state:
    active_requests: 0
    completed_requests_1min: 96
    error_rate_1min: 0.0
    avg_response_time_1min: 117.78388172388077
  metadata: {}
  efficiency:
    requests_per_second: 1.6
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.60
- **Baseline Value**: 0.10
- **Deviation**: 4.47 standard deviations
- **Change**: +1520.4%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 96
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 117.78ms

### Efficiency Metrics

- **Requests/sec**: 1.60
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.6,
    "baseline_value": 0.09873949579831932,
    "deviation": 4.468619666552001,
    "severity": "warning",
    "percentage_change": 1520.4255319148936
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 96,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 117.78388172388077
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.6,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
