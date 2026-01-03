---
timestamp: 1767379872.277924
datetime: '2026-01-02T13:51:12.277924'
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
  anomaly_id: avg_response_time_1min_1767379872.277924
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 471.4773169585637
    baseline_value: 639.5838596113962
    deviation: 3.6637200033288613
    severity: critical
    percentage_change: -26.283737484396823
  system_state:
    active_requests: 9
    completed_requests_1min: 784
    error_rate_1min: 0.0
    avg_response_time_1min: 471.4773169585637
  metadata: {}
  efficiency:
    requests_per_second: 13.066666666666666
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 471.48
- **Baseline Value**: 639.58
- **Deviation**: 3.66 standard deviations
- **Change**: -26.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 784
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 471.48ms

### Efficiency Metrics

- **Requests/sec**: 13.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 471.4773169585637,
    "baseline_value": 639.5838596113962,
    "deviation": 3.6637200033288613,
    "severity": "critical",
    "percentage_change": -26.283737484396823
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 784,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 471.4773169585637
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.066666666666666,
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
