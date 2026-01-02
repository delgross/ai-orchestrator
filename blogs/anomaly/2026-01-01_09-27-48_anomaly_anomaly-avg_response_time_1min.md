---
timestamp: 1767277668.9321442
datetime: '2026-01-01T09:27:48.932144'
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
  anomaly_id: avg_response_time_1min_1767277668.9321442
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 601.9595118536465
    baseline_value: 372.8222700265738
    deviation: 1.8739385968915216
    severity: warning
    percentage_change: 61.460180962564394
  system_state:
    active_requests: 0
    completed_requests_1min: 69
    error_rate_1min: 0.0
    avg_response_time_1min: 601.9595118536465
  metadata: {}
  efficiency:
    requests_per_second: 1.15
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 601.96
- **Baseline Value**: 372.82
- **Deviation**: 1.87 standard deviations
- **Change**: +61.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 69
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 601.96ms

### Efficiency Metrics

- **Requests/sec**: 1.15
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 601.9595118536465,
    "baseline_value": 372.8222700265738,
    "deviation": 1.8739385968915216,
    "severity": "warning",
    "percentage_change": 61.460180962564394
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 69,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 601.9595118536465
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.15,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
