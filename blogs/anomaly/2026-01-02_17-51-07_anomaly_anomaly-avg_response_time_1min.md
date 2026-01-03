---
timestamp: 1767394267.9790652
datetime: '2026-01-02T17:51:07.979065'
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
  anomaly_id: avg_response_time_1min_1767394267.9790652
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 437.57753138956815
    baseline_value: 357.4490209420522
    deviation: 3.048194777008319
    severity: critical
    percentage_change: 22.416765959055738
  system_state:
    active_requests: 2
    completed_requests_1min: 184
    error_rate_1min: 0.0
    avg_response_time_1min: 437.57753138956815
  metadata: {}
  efficiency:
    requests_per_second: 3.066666666666667
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 437.58
- **Baseline Value**: 357.45
- **Deviation**: 3.05 standard deviations
- **Change**: +22.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 184
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 437.58ms

### Efficiency Metrics

- **Requests/sec**: 3.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 437.57753138956815,
    "baseline_value": 357.4490209420522,
    "deviation": 3.048194777008319,
    "severity": "critical",
    "percentage_change": 22.416765959055738
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 184,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 437.57753138956815
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.066666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
