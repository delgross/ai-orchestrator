---
timestamp: 1767323620.740393
datetime: '2026-01-01T22:13:40.740393'
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
  anomaly_id: avg_response_time_1min_1767323620.740393
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 450.1577506549984
    baseline_value: 446.0024488834372
    deviation: 1.8306990448161624
    severity: warning
    percentage_change: 0.9316768959372211
  system_state:
    active_requests: 6
    completed_requests_1min: 797
    error_rate_1min: 0.0
    avg_response_time_1min: 450.1577506549984
  metadata: {}
  efficiency:
    requests_per_second: 13.283333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 450.16
- **Baseline Value**: 446.00
- **Deviation**: 1.83 standard deviations
- **Change**: +0.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 797
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 450.16ms

### Efficiency Metrics

- **Requests/sec**: 13.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 450.1577506549984,
    "baseline_value": 446.0024488834372,
    "deviation": 1.8306990448161624,
    "severity": "warning",
    "percentage_change": 0.9316768959372211
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 797,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 450.1577506549984
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.283333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
