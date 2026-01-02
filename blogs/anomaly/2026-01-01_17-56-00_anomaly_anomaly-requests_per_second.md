---
timestamp: 1767308160.987176
datetime: '2026-01-01T17:56:00.987176'
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
  anomaly_id: requests_per_second_1767308160.987176
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 7.083333333333333
    baseline_value: 3.15
    deviation: 1.6275862068965516
    severity: warning
    percentage_change: 124.86772486772486
  system_state:
    active_requests: 2
    completed_requests_1min: 425
    error_rate_1min: 0.0
    avg_response_time_1min: 223.07356273426728
  metadata: {}
  efficiency:
    requests_per_second: 7.083333333333333
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 7.08
- **Baseline Value**: 3.15
- **Deviation**: 1.63 standard deviations
- **Change**: +124.9%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 425
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 223.07ms

### Efficiency Metrics

- **Requests/sec**: 7.08
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 7.083333333333333,
    "baseline_value": 3.15,
    "deviation": 1.6275862068965516,
    "severity": "warning",
    "percentage_change": 124.86772486772486
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 425,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 223.07356273426728
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 7.083333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
