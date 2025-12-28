---
timestamp: 1766878924.9842
datetime: '2025-12-27T18:42:04.984200'
category: anomaly
severity: critical
title: 'Anomaly: active_requests'
source: anomaly_detector
tags:
- anomaly
- active_requests
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: active_requests_1766878924.9842
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 0.0
    baseline_value: 0.993
    deviation: 6.8569283935604535
    severity: critical
    percentage_change: -100.0
  system_state:
    active_requests: 0
    completed_requests_1min: 147
    error_rate_1min: 0.0
    avg_response_time_1min: 122.66528038751511
  metadata: {}
  efficiency:
    requests_per_second: 2.45
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 0.00
- **Baseline Value**: 0.99
- **Deviation**: 6.86 standard deviations
- **Change**: -100.0%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 147
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 122.67ms

### Efficiency Metrics

- **Requests/sec**: 2.45
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 0.0,
    "baseline_value": 0.993,
    "deviation": 6.8569283935604535,
    "severity": "critical",
    "percentage_change": -100.0
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 147,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 122.66528038751511
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.45,
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
