---
timestamp: 1767414226.153004
datetime: '2026-01-02T23:23:46.153004'
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
  anomaly_id: active_requests_1767414226.153004
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 18.0
    baseline_value: 2.0
    deviation: 8.0
    severity: critical
    percentage_change: 800.0
  system_state:
    active_requests: 18
    completed_requests_1min: 765
    error_rate_1min: 0.0
    avg_response_time_1min: 1191.239790199629
  metadata: {}
  efficiency:
    requests_per_second: 12.75
    cache_hit_rate: 0.0
    queue_depth: 18
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 18.00
- **Baseline Value**: 2.00
- **Deviation**: 8.00 standard deviations
- **Change**: +800.0%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 18
- **Completed Requests (1min)**: 765
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1191.24ms

### Efficiency Metrics

- **Requests/sec**: 12.75
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 18

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 18.0,
    "baseline_value": 2.0,
    "deviation": 8.0,
    "severity": "critical",
    "percentage_change": 800.0
  },
  "system_state": {
    "active_requests": 18,
    "completed_requests_1min": 765,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1191.239790199629
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.75,
    "cache_hit_rate": 0.0,
    "queue_depth": 18
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
