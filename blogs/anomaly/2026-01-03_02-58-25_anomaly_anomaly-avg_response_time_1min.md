---
timestamp: 1767427105.26706
datetime: '2026-01-03T02:58:25.267060'
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
  anomaly_id: avg_response_time_1min_1767427105.26706
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 595.7611883387846
    baseline_value: 563.1383356810315
    deviation: 5.267139282094944
    severity: critical
    percentage_change: 5.793044193714953
  system_state:
    active_requests: 6
    completed_requests_1min: 680
    error_rate_1min: 0.0
    avg_response_time_1min: 595.7611883387846
  metadata: {}
  efficiency:
    requests_per_second: 11.333333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 595.76
- **Baseline Value**: 563.14
- **Deviation**: 5.27 standard deviations
- **Change**: +5.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 680
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 595.76ms

### Efficiency Metrics

- **Requests/sec**: 11.33
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
    "current_value": 595.7611883387846,
    "baseline_value": 563.1383356810315,
    "deviation": 5.267139282094944,
    "severity": "critical",
    "percentage_change": 5.793044193714953
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 680,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 595.7611883387846
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.333333333333334,
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
