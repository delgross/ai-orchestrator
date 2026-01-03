---
timestamp: 1767404220.0625548
datetime: '2026-01-02T20:37:00.062555'
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
  anomaly_id: avg_response_time_1min_1767404220.0625548
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 364.590356295759
    baseline_value: 487.97282067393456
    deviation: 5.404654234974002
    severity: critical
    percentage_change: -25.284700120751236
  system_state:
    active_requests: 1
    completed_requests_1min: 176
    error_rate_1min: 0.0
    avg_response_time_1min: 364.590356295759
  metadata: {}
  efficiency:
    requests_per_second: 2.933333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 364.59
- **Baseline Value**: 487.97
- **Deviation**: 5.40 standard deviations
- **Change**: -25.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 176
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 364.59ms

### Efficiency Metrics

- **Requests/sec**: 2.93
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
    "current_value": 364.590356295759,
    "baseline_value": 487.97282067393456,
    "deviation": 5.404654234974002,
    "severity": "critical",
    "percentage_change": -25.284700120751236
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 176,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 364.590356295759
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.933333333333333,
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
