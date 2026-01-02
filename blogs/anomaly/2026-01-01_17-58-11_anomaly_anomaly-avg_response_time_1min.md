---
timestamp: 1767308291.1798642
datetime: '2026-01-01T17:58:11.179864'
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
  anomaly_id: avg_response_time_1min_1767308291.1798642
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 304.6623669879537
    baseline_value: 260.50716400146484
    deviation: 5.5922675746536195
    severity: critical
    percentage_change: 16.94970775784138
  system_state:
    active_requests: 1
    completed_requests_1min: 142
    error_rate_1min: 0.0
    avg_response_time_1min: 304.6623669879537
  metadata: {}
  efficiency:
    requests_per_second: 2.3666666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 304.66
- **Baseline Value**: 260.51
- **Deviation**: 5.59 standard deviations
- **Change**: +16.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 142
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 304.66ms

### Efficiency Metrics

- **Requests/sec**: 2.37
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
    "current_value": 304.6623669879537,
    "baseline_value": 260.50716400146484,
    "deviation": 5.5922675746536195,
    "severity": "critical",
    "percentage_change": 16.94970775784138
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 142,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 304.6623669879537
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.3666666666666667,
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
