---
timestamp: 1766886365.475724
datetime: '2025-12-27T20:46:05.475724'
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
  anomaly_id: requests_per_second_1766886365.475724
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.9666666666666667
    baseline_value: 2.4144666666666668
    deviation: 7.989917623323608
    severity: critical
    percentage_change: -59.96355302758373
  system_state:
    active_requests: 1
    completed_requests_1min: 58
    error_rate_1min: 0.0
    avg_response_time_1min: 39.34485336829876
  metadata: {}
  efficiency:
    requests_per_second: 0.9666666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.97
- **Baseline Value**: 2.41
- **Deviation**: 7.99 standard deviations
- **Change**: -60.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 58
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 39.34ms

### Efficiency Metrics

- **Requests/sec**: 0.97
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 0.9666666666666667,
    "baseline_value": 2.4144666666666668,
    "deviation": 7.989917623323608,
    "severity": "critical",
    "percentage_change": -59.96355302758373
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 58,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 39.34485336829876
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9666666666666667,
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
