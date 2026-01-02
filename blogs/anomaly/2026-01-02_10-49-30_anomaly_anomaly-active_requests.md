---
timestamp: 1767368970.9986649
datetime: '2026-01-02T10:49:30.998665'
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
  anomaly_id: active_requests_1767368970.9986649
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 13.0
    baseline_value: 18.0
    deviation: 5.0
    severity: critical
    percentage_change: -27.77777777777778
  system_state:
    active_requests: 13
    completed_requests_1min: 498
    error_rate_1min: 0.0
    avg_response_time_1min: 1101.496782647558
  metadata: {}
  efficiency:
    requests_per_second: 8.3
    cache_hit_rate: 0.0
    queue_depth: 13
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 13.00
- **Baseline Value**: 18.00
- **Deviation**: 5.00 standard deviations
- **Change**: -27.8%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 13
- **Completed Requests (1min)**: 498
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1101.50ms

### Efficiency Metrics

- **Requests/sec**: 8.30
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 13

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 13.0,
    "baseline_value": 18.0,
    "deviation": 5.0,
    "severity": "critical",
    "percentage_change": -27.77777777777778
  },
  "system_state": {
    "active_requests": 13,
    "completed_requests_1min": 498,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1101.496782647558
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 8.3,
    "cache_hit_rate": 0.0,
    "queue_depth": 13
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
