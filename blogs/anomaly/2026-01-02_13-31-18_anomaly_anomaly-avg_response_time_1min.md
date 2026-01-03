---
timestamp: 1767378678.016365
datetime: '2026-01-02T13:31:18.016365'
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
  anomaly_id: avg_response_time_1min_1767378678.016365
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 532.3935423943615
    baseline_value: 839.0568596633834
    deviation: 8.446918064433817
    severity: critical
    percentage_change: -36.548574001534355
  system_state:
    active_requests: 8
    completed_requests_1min: 793
    error_rate_1min: 0.0
    avg_response_time_1min: 532.3935423943615
  metadata: {}
  efficiency:
    requests_per_second: 13.216666666666667
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 532.39
- **Baseline Value**: 839.06
- **Deviation**: 8.45 standard deviations
- **Change**: -36.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 793
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 532.39ms

### Efficiency Metrics

- **Requests/sec**: 13.22
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 532.3935423943615,
    "baseline_value": 839.0568596633834,
    "deviation": 8.446918064433817,
    "severity": "critical",
    "percentage_change": -36.548574001534355
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 793,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 532.3935423943615
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.216666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
