---
timestamp: 1767295602.21181
datetime: '2026-01-01T14:26:42.211810'
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
  anomaly_id: avg_response_time_1min_1767295602.21181
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 407.8603624673414
    baseline_value: 617.6926969461051
    deviation: 5.030891737578828
    severity: critical
    percentage_change: -33.97034407500401
  system_state:
    active_requests: 7
    completed_requests_1min: 955
    error_rate_1min: 0.0
    avg_response_time_1min: 407.8603624673414
  metadata: {}
  efficiency:
    requests_per_second: 15.916666666666666
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 407.86
- **Baseline Value**: 617.69
- **Deviation**: 5.03 standard deviations
- **Change**: -34.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 955
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 407.86ms

### Efficiency Metrics

- **Requests/sec**: 15.92
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 407.8603624673414,
    "baseline_value": 617.6926969461051,
    "deviation": 5.030891737578828,
    "severity": "critical",
    "percentage_change": -33.97034407500401
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 955,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 407.8603624673414
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 15.916666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
