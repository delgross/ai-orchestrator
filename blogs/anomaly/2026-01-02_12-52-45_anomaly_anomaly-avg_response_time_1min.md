---
timestamp: 1767376365.727274
datetime: '2026-01-02T12:52:45.727274'
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
  anomaly_id: avg_response_time_1min_1767376365.727274
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 672.5069527850725
    baseline_value: 518.2432228266591
    deviation: 21.834731290984735
    severity: critical
    percentage_change: 29.766666145099048
  system_state:
    active_requests: 8
    completed_requests_1min: 764
    error_rate_1min: 0.0
    avg_response_time_1min: 672.5069527850725
  metadata: {}
  efficiency:
    requests_per_second: 12.733333333333333
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 672.51
- **Baseline Value**: 518.24
- **Deviation**: 21.83 standard deviations
- **Change**: +29.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 764
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 672.51ms

### Efficiency Metrics

- **Requests/sec**: 12.73
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
    "current_value": 672.5069527850725,
    "baseline_value": 518.2432228266591,
    "deviation": 21.834731290984735,
    "severity": "critical",
    "percentage_change": 29.766666145099048
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 764,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 672.5069527850725
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.733333333333333,
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
