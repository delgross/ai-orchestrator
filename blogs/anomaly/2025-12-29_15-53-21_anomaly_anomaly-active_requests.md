---
timestamp: 1767041601.706944
datetime: '2025-12-29T15:53:21.706944'
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
  anomaly_id: active_requests_1767041601.706944
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 5.0
    baseline_value: 0.16611295681063123
    deviation: 6.116361326020129
    severity: critical
    percentage_change: 2910.0
  system_state:
    active_requests: 5
    completed_requests_1min: 8
    error_rate_1min: 0.0
    avg_response_time_1min: 31866.672039031982
  metadata: {}
  efficiency:
    requests_per_second: 0.13333333333333333
    cache_hit_rate: 0.0
    queue_depth: 5
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 5.00
- **Baseline Value**: 0.17
- **Deviation**: 6.12 standard deviations
- **Change**: +2910.0%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 5
- **Completed Requests (1min)**: 8
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 31866.67ms

### Efficiency Metrics

- **Requests/sec**: 0.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 5

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 5.0,
    "baseline_value": 0.16611295681063123,
    "deviation": 6.116361326020129,
    "severity": "critical",
    "percentage_change": 2910.0
  },
  "system_state": {
    "active_requests": 5,
    "completed_requests_1min": 8,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 31866.672039031982
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.13333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 5
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
