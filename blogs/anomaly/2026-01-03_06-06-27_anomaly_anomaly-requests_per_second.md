---
timestamp: 1767438387.666647
datetime: '2026-01-03T06:06:27.666647'
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
  anomaly_id: requests_per_second_1767438387.666647
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 10.8
    baseline_value: 11.5
    deviation: 4.666666666666651
    severity: critical
    percentage_change: -6.086956521739125
  system_state:
    active_requests: 6
    completed_requests_1min: 648
    error_rate_1min: 0.0
    avg_response_time_1min: 553.9584656556448
  metadata: {}
  efficiency:
    requests_per_second: 10.8
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 10.80
- **Baseline Value**: 11.50
- **Deviation**: 4.67 standard deviations
- **Change**: -6.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 648
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 553.96ms

### Efficiency Metrics

- **Requests/sec**: 10.80
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 10.8,
    "baseline_value": 11.5,
    "deviation": 4.666666666666651,
    "severity": "critical",
    "percentage_change": -6.086956521739125
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 648,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 553.9584656556448
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.8,
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
