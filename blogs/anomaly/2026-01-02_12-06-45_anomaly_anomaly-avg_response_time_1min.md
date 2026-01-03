---
timestamp: 1767373605.167543
datetime: '2026-01-02T12:06:45.167543'
category: anomaly
severity: critical
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767373605.167543
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 766.8847357807447
    baseline_value: 532.6728726648221
    deviation: 6.115675611783543
    severity: critical
    percentage_change: 43.96917416579191
  system_state:
    active_requests: 9
    completed_requests_1min: 796
    error_rate_1min: 0.0
    avg_response_time_1min: 766.8847357807447
  metadata: {}
  efficiency:
    requests_per_second: 13.266666666666667
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 766.88
- **Baseline Value**: 532.67
- **Deviation**: 6.12 standard deviations
- **Change**: +44.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 796
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 766.88ms

### Efficiency Metrics

- **Requests/sec**: 13.27
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 766.8847357807447,
    "baseline_value": 532.6728726648221,
    "deviation": 6.115675611783543,
    "severity": "critical",
    "percentage_change": 43.96917416579191
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 796,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 766.8847357807447
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.266666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
