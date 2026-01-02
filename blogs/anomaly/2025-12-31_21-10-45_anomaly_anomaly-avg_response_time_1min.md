---
timestamp: 1767233445.3041558
datetime: '2025-12-31T21:10:45.304156'
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
  anomaly_id: avg_response_time_1min_1767233445.3041558
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 210.95071684929633
    baseline_value: 183.04609867834276
    deviation: 1.8536254411184316
    severity: warning
    percentage_change: 15.244585037558696
  system_state:
    active_requests: 1
    completed_requests_1min: 62
    error_rate_1min: 0.0
    avg_response_time_1min: 210.95071684929633
  metadata: {}
  efficiency:
    requests_per_second: 1.0333333333333334
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 210.95
- **Baseline Value**: 183.05
- **Deviation**: 1.85 standard deviations
- **Change**: +15.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 62
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 210.95ms

### Efficiency Metrics

- **Requests/sec**: 1.03
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 210.95071684929633,
    "baseline_value": 183.04609867834276,
    "deviation": 1.8536254411184316,
    "severity": "warning",
    "percentage_change": 15.244585037558696
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 62,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 210.95071684929633
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
