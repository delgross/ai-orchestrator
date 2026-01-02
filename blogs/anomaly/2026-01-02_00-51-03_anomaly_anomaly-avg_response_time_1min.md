---
timestamp: 1767333063.9096398
datetime: '2026-01-02T00:51:03.909640'
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
  anomaly_id: avg_response_time_1min_1767333063.9096398
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1836.248450809055
    baseline_value: 1069.9095249176025
    deviation: 1.7850310169991752
    severity: warning
    percentage_change: 71.6265168263149
  system_state:
    active_requests: 0
    completed_requests_1min: 9
    error_rate_1min: 0.0
    avg_response_time_1min: 1836.248450809055
  metadata: {}
  efficiency:
    requests_per_second: 0.15
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1836.25
- **Baseline Value**: 1069.91
- **Deviation**: 1.79 standard deviations
- **Change**: +71.6%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 9
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1836.25ms

### Efficiency Metrics

- **Requests/sec**: 0.15
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1836.248450809055,
    "baseline_value": 1069.9095249176025,
    "deviation": 1.7850310169991752,
    "severity": "warning",
    "percentage_change": 71.6265168263149
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 9,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1836.248450809055
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.15,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
