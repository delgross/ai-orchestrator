---
timestamp: 1767288728.778254
datetime: '2026-01-01T12:32:08.778254'
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
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767288728.778254
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1007.7315260854999
    baseline_value: 163.12725647636083
    deviation: 25.075096521348783
    severity: critical
    percentage_change: 517.7579074478782
  system_state:
    active_requests: 2
    completed_requests_1min: 89
    error_rate_1min: 0.0
    avg_response_time_1min: 1007.7315260854999
  metadata: {}
  efficiency:
    requests_per_second: 1.4833333333333334
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1007.73
- **Baseline Value**: 163.13
- **Deviation**: 25.08 standard deviations
- **Change**: +517.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 89
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1007.73ms

### Efficiency Metrics

- **Requests/sec**: 1.48
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1007.7315260854999,
    "baseline_value": 163.12725647636083,
    "deviation": 25.075096521348783,
    "severity": "critical",
    "percentage_change": 517.7579074478782
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 89,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1007.7315260854999
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.4833333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected
