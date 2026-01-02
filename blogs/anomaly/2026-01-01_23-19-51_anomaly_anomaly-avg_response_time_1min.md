---
timestamp: 1767327591.970436
datetime: '2026-01-01T23:19:51.970436'
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
  anomaly_id: avg_response_time_1min_1767327591.970436
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1.084819753119286
    baseline_value: 211.3091548283895
    deviation: 12.100143347503407
    severity: critical
    percentage_change: -99.48661961475341
  system_state:
    active_requests: 0
    completed_requests_1min: 94
    error_rate_1min: 0.0
    avg_response_time_1min: 1.084819753119286
  metadata: {}
  efficiency:
    requests_per_second: 1.5666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1.08
- **Baseline Value**: 211.31
- **Deviation**: 12.10 standard deviations
- **Change**: -99.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 94
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1.08ms

### Efficiency Metrics

- **Requests/sec**: 1.57
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1.084819753119286,
    "baseline_value": 211.3091548283895,
    "deviation": 12.100143347503407,
    "severity": "critical",
    "percentage_change": -99.48661961475341
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 94,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1.084819753119286
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.5666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
