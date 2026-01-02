---
timestamp: 1767327291.9218519
datetime: '2026-01-01T23:14:51.921852'
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
  anomaly_id: avg_response_time_1min_1767327291.9218519
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 0.9724696477254232
    baseline_value: 211.3091548283895
    deviation: 12.10661002216258
    severity: critical
    percentage_change: -99.53978820817527
  system_state:
    active_requests: 0
    completed_requests_1min: 48
    error_rate_1min: 0.0
    avg_response_time_1min: 0.9724696477254232
  metadata: {}
  efficiency:
    requests_per_second: 0.8
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 0.97
- **Baseline Value**: 211.31
- **Deviation**: 12.11 standard deviations
- **Change**: -99.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 48
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 0.97ms

### Efficiency Metrics

- **Requests/sec**: 0.80
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
    "current_value": 0.9724696477254232,
    "baseline_value": 211.3091548283895,
    "deviation": 12.10661002216258,
    "severity": "critical",
    "percentage_change": -99.53978820817527
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 48,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 0.9724696477254232
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.8,
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
