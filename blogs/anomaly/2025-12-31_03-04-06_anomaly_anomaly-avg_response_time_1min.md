---
timestamp: 1767168246.8788888
datetime: '2025-12-31T03:04:06.878889'
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
  anomaly_id: avg_response_time_1min_1767168246.8788888
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 115.05126953125
    baseline_value: 99.9793224647397
    deviation: 1.865139741732871
    severity: warning
    percentage_change: 15.075064218229542
  system_state:
    active_requests: 0
    completed_requests_1min: 12
    error_rate_1min: 0.0
    avg_response_time_1min: 115.05126953125
  metadata: {}
  efficiency:
    requests_per_second: 0.2
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 115.05
- **Baseline Value**: 99.98
- **Deviation**: 1.87 standard deviations
- **Change**: +15.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 12
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 115.05ms

### Efficiency Metrics

- **Requests/sec**: 0.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 115.05126953125,
    "baseline_value": 99.9793224647397,
    "deviation": 1.865139741732871,
    "severity": "warning",
    "percentage_change": 15.075064218229542
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 12,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 115.05126953125
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
