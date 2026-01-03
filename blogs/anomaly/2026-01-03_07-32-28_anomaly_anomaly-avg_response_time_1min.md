---
timestamp: 1767443548.873609
datetime: '2026-01-03T07:32:28.873609'
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
  anomaly_id: avg_response_time_1min_1767443548.873609
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 548.4846119894339
    baseline_value: 539.140758630529
    deviation: 1.5692155408599808
    severity: warning
    percentage_change: 1.7331009034893214
  system_state:
    active_requests: 6
    completed_requests_1min: 698
    error_rate_1min: 0.0
    avg_response_time_1min: 548.4846119894339
  metadata: {}
  efficiency:
    requests_per_second: 11.633333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 548.48
- **Baseline Value**: 539.14
- **Deviation**: 1.57 standard deviations
- **Change**: +1.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 698
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 548.48ms

### Efficiency Metrics

- **Requests/sec**: 11.63
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 548.4846119894339,
    "baseline_value": 539.140758630529,
    "deviation": 1.5692155408599808,
    "severity": "warning",
    "percentage_change": 1.7331009034893214
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 698,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 548.4846119894339
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.633333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
