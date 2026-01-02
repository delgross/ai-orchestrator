---
timestamp: 1767364229.792161
datetime: '2026-01-02T09:30:29.792161'
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
  anomaly_id: requests_per_second_1767364229.792161
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 7.55
    baseline_value: 0.2833333333333333
    deviation: 43.6
    severity: critical
    percentage_change: 2564.7058823529414
  system_state:
    active_requests: 9
    completed_requests_1min: 453
    error_rate_1min: 0.0
    avg_response_time_1min: 1302.851444838063
  metadata: {}
  efficiency:
    requests_per_second: 7.55
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 7.55
- **Baseline Value**: 0.28
- **Deviation**: 43.60 standard deviations
- **Change**: +2564.7%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 453
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1302.85ms

### Efficiency Metrics

- **Requests/sec**: 7.55
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 7.55,
    "baseline_value": 0.2833333333333333,
    "deviation": 43.6,
    "severity": "critical",
    "percentage_change": 2564.7058823529414
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 453,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1302.851444838063
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 7.55,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
