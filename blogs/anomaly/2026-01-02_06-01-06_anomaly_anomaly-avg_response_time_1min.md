---
timestamp: 1767351666.442504
datetime: '2026-01-02T06:01:06.442504'
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
  anomaly_id: avg_response_time_1min_1767351666.442504
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 463.0501644171334
    baseline_value: 500.9786781058254
    deviation: 5.620942806174759
    severity: critical
    percentage_change: -7.570883821263168
  system_state:
    active_requests: 6
    completed_requests_1min: 829
    error_rate_1min: 0.0
    avg_response_time_1min: 463.0501644171334
  metadata: {}
  efficiency:
    requests_per_second: 13.816666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 463.05
- **Baseline Value**: 500.98
- **Deviation**: 5.62 standard deviations
- **Change**: -7.6%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 829
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 463.05ms

### Efficiency Metrics

- **Requests/sec**: 13.82
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
    "current_value": 463.0501644171334,
    "baseline_value": 500.9786781058254,
    "deviation": 5.620942806174759,
    "severity": "critical",
    "percentage_change": -7.570883821263168
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 829,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 463.0501644171334
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.816666666666666,
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
