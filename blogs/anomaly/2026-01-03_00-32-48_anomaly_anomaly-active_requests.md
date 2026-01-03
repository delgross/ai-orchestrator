---
timestamp: 1767418368.4489212
datetime: '2026-01-03T00:32:48.448921'
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
  anomaly_id: active_requests_1767418368.4489212
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 21.0
    baseline_value: 29.0
    deviation: 4.0
    severity: critical
    percentage_change: -27.586206896551722
  system_state:
    active_requests: 21
    completed_requests_1min: 1947
    error_rate_1min: 0.0
    avg_response_time_1min: 947.6519909404643
  metadata: {}
  efficiency:
    requests_per_second: 32.45
    cache_hit_rate: 0.0
    queue_depth: 21
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 21.00
- **Baseline Value**: 29.00
- **Deviation**: 4.00 standard deviations
- **Change**: -27.6%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 21
- **Completed Requests (1min)**: 1947
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 947.65ms

### Efficiency Metrics

- **Requests/sec**: 32.45
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 21

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 21.0,
    "baseline_value": 29.0,
    "deviation": 4.0,
    "severity": "critical",
    "percentage_change": -27.586206896551722
  },
  "system_state": {
    "active_requests": 21,
    "completed_requests_1min": 1947,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 947.6519909404643
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 32.45,
    "cache_hit_rate": 0.0,
    "queue_depth": 21
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
