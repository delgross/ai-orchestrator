---
timestamp: 1767414826.563224
datetime: '2026-01-02T23:33:46.563224'
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
  anomaly_id: active_requests_1767414826.563224
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 20.0
    baseline_value: 2.0
    deviation: 9.0
    severity: critical
    percentage_change: 900.0
  system_state:
    active_requests: 20
    completed_requests_1min: 774
    error_rate_1min: 0.0
    avg_response_time_1min: 1616.0569499013343
  metadata: {}
  efficiency:
    requests_per_second: 12.9
    cache_hit_rate: 0.0
    queue_depth: 20
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 20.00
- **Baseline Value**: 2.00
- **Deviation**: 9.00 standard deviations
- **Change**: +900.0%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 20
- **Completed Requests (1min)**: 774
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1616.06ms

### Efficiency Metrics

- **Requests/sec**: 12.90
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 20

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 20.0,
    "baseline_value": 2.0,
    "deviation": 9.0,
    "severity": "critical",
    "percentage_change": 900.0
  },
  "system_state": {
    "active_requests": 20,
    "completed_requests_1min": 774,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1616.0569499013343
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.9,
    "cache_hit_rate": 0.0,
    "queue_depth": 20
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
