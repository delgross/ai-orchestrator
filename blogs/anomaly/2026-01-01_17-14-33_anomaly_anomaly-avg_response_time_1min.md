---
timestamp: 1767305673.139804
datetime: '2026-01-01T17:14:33.139804'
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
  anomaly_id: avg_response_time_1min_1767305673.139804
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 350.30394172668457
    baseline_value: 290.42149782180786
    deviation: 3.523121926058681
    severity: critical
    percentage_change: 20.619149874923657
  system_state:
    active_requests: 2
    completed_requests_1min: 125
    error_rate_1min: 0.0
    avg_response_time_1min: 350.30394172668457
  metadata: {}
  efficiency:
    requests_per_second: 2.0833333333333335
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 350.30
- **Baseline Value**: 290.42
- **Deviation**: 3.52 standard deviations
- **Change**: +20.6%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 125
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 350.30ms

### Efficiency Metrics

- **Requests/sec**: 2.08
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 350.30394172668457,
    "baseline_value": 290.42149782180786,
    "deviation": 3.523121926058681,
    "severity": "critical",
    "percentage_change": 20.619149874923657
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 125,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 350.30394172668457
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.0833333333333335,
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
