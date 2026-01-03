---
timestamp: 1767446129.296441
datetime: '2026-01-03T08:15:29.296441'
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
  anomaly_id: avg_response_time_1min_1767446129.296441
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 390.42658465249195
    baseline_value: 488.4640534121291
    deviation: 4.624447082836872
    severity: critical
    percentage_change: -20.070559558027604
  system_state:
    active_requests: 1
    completed_requests_1min: 140
    error_rate_1min: 0.0
    avg_response_time_1min: 390.42658465249195
  metadata: {}
  efficiency:
    requests_per_second: 2.3333333333333335
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 390.43
- **Baseline Value**: 488.46
- **Deviation**: 4.62 standard deviations
- **Change**: -20.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 140
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 390.43ms

### Efficiency Metrics

- **Requests/sec**: 2.33
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
    "current_value": 390.42658465249195,
    "baseline_value": 488.4640534121291,
    "deviation": 4.624447082836872,
    "severity": "critical",
    "percentage_change": -20.070559558027604
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 140,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 390.42658465249195
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.3333333333333335,
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
