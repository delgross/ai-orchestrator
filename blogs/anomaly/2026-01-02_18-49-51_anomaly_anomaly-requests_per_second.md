---
timestamp: 1767397791.202341
datetime: '2026-01-02T18:49:51.202341'
category: anomaly
severity: critical
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: requests_per_second_1767397791.202341
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 8.216666666666667
    baseline_value: 13.666666666666666
    deviation: 9.08333333333331
    severity: critical
    percentage_change: -39.8780487804878
  system_state:
    active_requests: 6
    completed_requests_1min: 493
    error_rate_1min: 0.0
    avg_response_time_1min: 722.8277406634472
  metadata: {}
  efficiency:
    requests_per_second: 8.216666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 8.22
- **Baseline Value**: 13.67
- **Deviation**: 9.08 standard deviations
- **Change**: -39.9%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 493
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 722.83ms

### Efficiency Metrics

- **Requests/sec**: 8.22
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 8.216666666666667,
    "baseline_value": 13.666666666666666,
    "deviation": 9.08333333333331,
    "severity": "critical",
    "percentage_change": -39.8780487804878
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 493,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 722.8277406634472
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 8.216666666666667,
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
