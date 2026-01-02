---
timestamp: 1767294522.1097522
datetime: '2026-01-01T14:08:42.109752'
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
  anomaly_id: avg_response_time_1min_1767294522.1097522
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 668.4167017702197
    baseline_value: 499.455232729857
    deviation: 3.6799065442490795
    severity: critical
    percentage_change: 33.82915183746803
  system_state:
    active_requests: 8
    completed_requests_1min: 610
    error_rate_1min: 0.0
    avg_response_time_1min: 668.4167017702197
  metadata: {}
  efficiency:
    requests_per_second: 10.166666666666666
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 668.42
- **Baseline Value**: 499.46
- **Deviation**: 3.68 standard deviations
- **Change**: +33.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 610
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 668.42ms

### Efficiency Metrics

- **Requests/sec**: 10.17
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
    "current_value": 668.4167017702197,
    "baseline_value": 499.455232729857,
    "deviation": 3.6799065442490795,
    "severity": "critical",
    "percentage_change": 33.82915183746803
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 610,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 668.4167017702197
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.166666666666666,
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
