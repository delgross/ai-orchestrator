---
timestamp: 1766835350.335402
datetime: '2025-12-27T06:35:50.335402'
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
  anomaly_id: requests_per_second_1766835350.335402
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.03333333333333333
    baseline_value: 0.01662721893491124
    deviation: 11.89306209643517
    severity: critical
    percentage_change: 100.47449584816135
  system_state:
    active_requests: 0
    completed_requests_1min: 2
    error_rate_1min: 0.0
    avg_response_time_1min: 3.8944482803344727
  metadata: {}
  efficiency:
    requests_per_second: 0.03333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.03
- **Baseline Value**: 0.02
- **Deviation**: 11.89 standard deviations
- **Change**: +100.5%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 2
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 3.89ms

### Efficiency Metrics

- **Requests/sec**: 0.03
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
    "current_value": 0.03333333333333333,
    "baseline_value": 0.01662721893491124,
    "deviation": 11.89306209643517,
    "severity": "critical",
    "percentage_change": 100.47449584816135
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 2,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 3.8944482803344727
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.03333333333333333,
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
