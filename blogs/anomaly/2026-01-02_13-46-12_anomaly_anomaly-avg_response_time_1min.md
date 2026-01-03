---
timestamp: 1767379572.151362
datetime: '2026-01-02T13:46:12.151362'
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
  anomaly_id: avg_response_time_1min_1767379572.151362
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 541.3560732237121
    baseline_value: 482.9797654014247
    deviation: 2.1370714482540296
    severity: warning
    percentage_change: 12.086698450766029
  system_state:
    active_requests: 8
    completed_requests_1min: 759
    error_rate_1min: 0.0
    avg_response_time_1min: 541.3560732237121
  metadata: {}
  efficiency:
    requests_per_second: 12.65
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 541.36
- **Baseline Value**: 482.98
- **Deviation**: 2.14 standard deviations
- **Change**: +12.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 759
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 541.36ms

### Efficiency Metrics

- **Requests/sec**: 12.65
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 541.3560732237121,
    "baseline_value": 482.9797654014247,
    "deviation": 2.1370714482540296,
    "severity": "warning",
    "percentage_change": 12.086698450766029
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 759,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 541.3560732237121
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.65,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
