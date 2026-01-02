---
timestamp: 1767346265.58145
datetime: '2026-01-02T04:31:05.581450'
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
  anomaly_id: avg_response_time_1min_1767346265.58145
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 442.0386945364262
    baseline_value: 434.3005479245946
    deviation: 6.138239198495951
    severity: critical
    percentage_change: 1.7817492169443787
  system_state:
    active_requests: 6
    completed_requests_1min: 826
    error_rate_1min: 0.0
    avg_response_time_1min: 442.0386945364262
  metadata: {}
  efficiency:
    requests_per_second: 13.766666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 442.04
- **Baseline Value**: 434.30
- **Deviation**: 6.14 standard deviations
- **Change**: +1.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 826
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 442.04ms

### Efficiency Metrics

- **Requests/sec**: 13.77
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 442.0386945364262,
    "baseline_value": 434.3005479245946,
    "deviation": 6.138239198495951,
    "severity": "critical",
    "percentage_change": 1.7817492169443787
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 826,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 442.0386945364262
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.766666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
