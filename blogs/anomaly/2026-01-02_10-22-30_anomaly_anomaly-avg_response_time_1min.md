---
timestamp: 1767367350.617331
datetime: '2026-01-02T10:22:30.617331'
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
  anomaly_id: avg_response_time_1min_1767367350.617331
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 987.7366991100197
    baseline_value: 1480.203287040486
    deviation: 1.719301511542065
    severity: warning
    percentage_change: -33.2701995896187
  system_state:
    active_requests: 22
    completed_requests_1min: 668
    error_rate_1min: 0.0
    avg_response_time_1min: 987.7366991100197
  metadata: {}
  efficiency:
    requests_per_second: 11.133333333333333
    cache_hit_rate: 0.0
    queue_depth: 22
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 987.74
- **Baseline Value**: 1480.20
- **Deviation**: 1.72 standard deviations
- **Change**: -33.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 22
- **Completed Requests (1min)**: 668
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 987.74ms

### Efficiency Metrics

- **Requests/sec**: 11.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 22

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 987.7366991100197,
    "baseline_value": 1480.203287040486,
    "deviation": 1.719301511542065,
    "severity": "warning",
    "percentage_change": -33.2701995896187
  },
  "system_state": {
    "active_requests": 22,
    "completed_requests_1min": 668,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 987.7366991100197
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.133333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 22
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
