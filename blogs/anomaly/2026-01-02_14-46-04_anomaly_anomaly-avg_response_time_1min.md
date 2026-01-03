---
timestamp: 1767383164.394814
datetime: '2026-01-02T14:46:04.394814'
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
  anomaly_id: avg_response_time_1min_1767383164.394814
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 9110.708973624489
    baseline_value: 765.8302913954917
    deviation: 262.1198981734858
    severity: critical
    percentage_change: 1089.6511637092606
  system_state:
    active_requests: 2
    completed_requests_1min: 11
    error_rate_1min: 0.0
    avg_response_time_1min: 9110.708973624489
  metadata: {}
  efficiency:
    requests_per_second: 0.18333333333333332
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 9110.71
- **Baseline Value**: 765.83
- **Deviation**: 262.12 standard deviations
- **Change**: +1089.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 11
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 9110.71ms

### Efficiency Metrics

- **Requests/sec**: 0.18
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
    "current_value": 9110.708973624489,
    "baseline_value": 765.8302913954917,
    "deviation": 262.1198981734858,
    "severity": "critical",
    "percentage_change": 1089.6511637092606
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 11,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 9110.708973624489
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.18333333333333332,
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
