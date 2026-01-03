---
timestamp: 1767378828.714912
datetime: '2026-01-02T13:33:48.714912'
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
  anomaly_id: avg_response_time_1min_1767378828.714912
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 532.2366525901459
    baseline_value: 491.79667448711774
    deviation: 3.0617364015414985
    severity: critical
    percentage_change: 8.222905969260976
  system_state:
    active_requests: 8
    completed_requests_1min: 751
    error_rate_1min: 0.0
    avg_response_time_1min: 532.2366525901459
  metadata: {}
  efficiency:
    requests_per_second: 12.516666666666667
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 532.24
- **Baseline Value**: 491.80
- **Deviation**: 3.06 standard deviations
- **Change**: +8.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 751
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 532.24ms

### Efficiency Metrics

- **Requests/sec**: 12.52
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
    "current_value": 532.2366525901459,
    "baseline_value": 491.79667448711774,
    "deviation": 3.0617364015414985,
    "severity": "critical",
    "percentage_change": 8.222905969260976
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 751,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 532.2366525901459
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.516666666666667,
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
