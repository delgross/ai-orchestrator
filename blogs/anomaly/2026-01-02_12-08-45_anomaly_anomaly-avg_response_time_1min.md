---
timestamp: 1767373725.211332
datetime: '2026-01-02T12:08:45.211332'
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
  anomaly_id: avg_response_time_1min_1767373725.211332
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 518.1839902593632
    baseline_value: 684.0807193620199
    deviation: 2.3298059503843973
    severity: warning
    percentage_change: -24.25104587911402
  system_state:
    active_requests: 10
    completed_requests_1min: 792
    error_rate_1min: 0.0
    avg_response_time_1min: 518.1839902593632
  metadata: {}
  efficiency:
    requests_per_second: 13.2
    cache_hit_rate: 0.0
    queue_depth: 10
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 518.18
- **Baseline Value**: 684.08
- **Deviation**: 2.33 standard deviations
- **Change**: -24.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 10
- **Completed Requests (1min)**: 792
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 518.18ms

### Efficiency Metrics

- **Requests/sec**: 13.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 10

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 518.1839902593632,
    "baseline_value": 684.0807193620199,
    "deviation": 2.3298059503843973,
    "severity": "warning",
    "percentage_change": -24.25104587911402
  },
  "system_state": {
    "active_requests": 10,
    "completed_requests_1min": 792,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 518.1839902593632
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 10
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
