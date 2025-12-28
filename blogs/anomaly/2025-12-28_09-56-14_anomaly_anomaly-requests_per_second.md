---
timestamp: 1766933774.1139688
datetime: '2025-12-28T09:56:14.113969'
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
  anomaly_id: requests_per_second_1766933774.1139688
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 9.333333333333334
    baseline_value: 0.9034274193548387
    deviation: 71.12664640445858
    severity: critical
    percentage_change: 933.1027300453767
  system_state:
    active_requests: 0
    completed_requests_1min: 560
    error_rate_1min: 0.0
    avg_response_time_1min: 46.69062239783151
  metadata: {}
  efficiency:
    requests_per_second: 9.333333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 9.33
- **Baseline Value**: 0.90
- **Deviation**: 71.13 standard deviations
- **Change**: +933.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 560
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 46.69ms

### Efficiency Metrics

- **Requests/sec**: 9.33
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 9.333333333333334,
    "baseline_value": 0.9034274193548387,
    "deviation": 71.12664640445858,
    "severity": "critical",
    "percentage_change": 933.1027300453767
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 560,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 46.69062239783151
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 9.333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
