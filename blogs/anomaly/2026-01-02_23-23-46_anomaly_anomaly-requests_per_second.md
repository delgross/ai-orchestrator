---
timestamp: 1767414226.1764858
datetime: '2026-01-02T23:23:46.176486'
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
  anomaly_id: requests_per_second_1767414226.1764858
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 12.75
    baseline_value: 0.1
    deviation: 151.79999999999998
    severity: critical
    percentage_change: 12650.0
  system_state:
    active_requests: 18
    completed_requests_1min: 765
    error_rate_1min: 0.0
    avg_response_time_1min: 1191.239790199629
  metadata: {}
  efficiency:
    requests_per_second: 12.75
    cache_hit_rate: 0.0
    queue_depth: 18
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 12.75
- **Baseline Value**: 0.10
- **Deviation**: 151.80 standard deviations
- **Change**: +12650.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 18
- **Completed Requests (1min)**: 765
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1191.24ms

### Efficiency Metrics

- **Requests/sec**: 12.75
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 18

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 12.75,
    "baseline_value": 0.1,
    "deviation": 151.79999999999998,
    "severity": "critical",
    "percentage_change": 12650.0
  },
  "system_state": {
    "active_requests": 18,
    "completed_requests_1min": 765,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1191.239790199629
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.75,
    "cache_hit_rate": 0.0,
    "queue_depth": 18
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
