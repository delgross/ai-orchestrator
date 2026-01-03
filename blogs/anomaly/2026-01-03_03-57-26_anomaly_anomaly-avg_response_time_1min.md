---
timestamp: 1767430646.043898
datetime: '2026-01-03T03:57:26.043898'
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
  anomaly_id: avg_response_time_1min_1767430646.043898
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 550.3794961388766
    baseline_value: 532.770856221517
    deviation: 2.353266327812487
    severity: warning
    percentage_change: 3.3051056963292726
  system_state:
    active_requests: 6
    completed_requests_1min: 681
    error_rate_1min: 0.0
    avg_response_time_1min: 550.3794961388766
  metadata: {}
  efficiency:
    requests_per_second: 11.35
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 550.38
- **Baseline Value**: 532.77
- **Deviation**: 2.35 standard deviations
- **Change**: +3.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 681
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 550.38ms

### Efficiency Metrics

- **Requests/sec**: 11.35
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 550.3794961388766,
    "baseline_value": 532.770856221517,
    "deviation": 2.353266327812487,
    "severity": "warning",
    "percentage_change": 3.3051056963292726
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 681,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 550.3794961388766
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.35,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
