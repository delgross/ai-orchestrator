---
timestamp: 1767356970.882058
datetime: '2026-01-02T07:29:30.882058'
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
  anomaly_id: avg_response_time_1min_1767356970.882058
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 200.6579256549324
    baseline_value: 674.3912787262619
    deviation: 3.386655909336314
    severity: critical
    percentage_change: -70.2460675301259
  system_state:
    active_requests: 4
    completed_requests_1min: 582
    error_rate_1min: 0.0
    avg_response_time_1min: 200.6579256549324
  metadata: {}
  efficiency:
    requests_per_second: 9.7
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 200.66
- **Baseline Value**: 674.39
- **Deviation**: 3.39 standard deviations
- **Change**: -70.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 582
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 200.66ms

### Efficiency Metrics

- **Requests/sec**: 9.70
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 200.6579256549324,
    "baseline_value": 674.3912787262619,
    "deviation": 3.386655909336314,
    "severity": "critical",
    "percentage_change": -70.2460675301259
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 582,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 200.6579256549324
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 9.7,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
