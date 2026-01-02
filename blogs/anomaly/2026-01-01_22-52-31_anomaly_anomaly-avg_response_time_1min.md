---
timestamp: 1767325951.578923
datetime: '2026-01-01T22:52:31.578923'
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
  anomaly_id: avg_response_time_1min_1767325951.578923
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 361.1701260442319
    baseline_value: 278.2286715834108
    deviation: 3.9920133119909154
    severity: critical
    percentage_change: 29.810534618448152
  system_state:
    active_requests: 1
    completed_requests_1min: 115
    error_rate_1min: 0.0
    avg_response_time_1min: 361.1701260442319
  metadata: {}
  efficiency:
    requests_per_second: 1.9166666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 361.17
- **Baseline Value**: 278.23
- **Deviation**: 3.99 standard deviations
- **Change**: +29.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 115
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 361.17ms

### Efficiency Metrics

- **Requests/sec**: 1.92
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 361.1701260442319,
    "baseline_value": 278.2286715834108,
    "deviation": 3.9920133119909154,
    "severity": "critical",
    "percentage_change": 29.810534618448152
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 115,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 361.1701260442319
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.9166666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
