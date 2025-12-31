---
timestamp: 1767152224.472218
datetime: '2025-12-30T22:37:04.472218'
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
  anomaly_id: avg_response_time_1min_1767152224.472218
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 95.48581019043922
    baseline_value: 85.23501210267159
    deviation: 3.5998963231103605
    severity: critical
    percentage_change: 12.026510978164495
  system_state:
    active_requests: 0
    completed_requests_1min: 128
    error_rate_1min: 0.0
    avg_response_time_1min: 95.48581019043922
  metadata: {}
  efficiency:
    requests_per_second: 2.1333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 95.49
- **Baseline Value**: 85.24
- **Deviation**: 3.60 standard deviations
- **Change**: +12.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 128
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 95.49ms

### Efficiency Metrics

- **Requests/sec**: 2.13
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
    "current_value": 95.48581019043922,
    "baseline_value": 85.23501210267159,
    "deviation": 3.5998963231103605,
    "severity": "critical",
    "percentage_change": 12.026510978164495
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 128,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 95.48581019043922
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.1333333333333333,
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
