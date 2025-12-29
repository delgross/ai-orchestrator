---
timestamp: 1767044061.827189
datetime: '2025-12-29T16:34:21.827189'
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
  anomaly_id: requests_per_second_1767044061.827189
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.75
    baseline_value: 0.02919103313840156
    deviation: 36.639074054692195
    severity: critical
    percentage_change: 5894.991652754591
  system_state:
    active_requests: 2
    completed_requests_1min: 105
    error_rate_1min: 0.0
    avg_response_time_1min: 1328.7756057012648
  metadata: {}
  efficiency:
    requests_per_second: 1.75
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.75
- **Baseline Value**: 0.03
- **Deviation**: 36.64 standard deviations
- **Change**: +5895.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 105
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1328.78ms

### Efficiency Metrics

- **Requests/sec**: 1.75
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.75,
    "baseline_value": 0.02919103313840156,
    "deviation": 36.639074054692195,
    "severity": "critical",
    "percentage_change": 5894.991652754591
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 105,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1328.7756057012648
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.75,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
