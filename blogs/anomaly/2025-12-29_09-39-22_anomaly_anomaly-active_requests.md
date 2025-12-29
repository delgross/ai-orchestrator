---
timestamp: 1767019162.761578
datetime: '2025-12-29T09:39:22.761578'
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
  anomaly_id: active_requests_1767019162.761578
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 3.0
    baseline_value: 0.18888888888888888
    deviation: 6.30543594458351
    severity: critical
    percentage_change: 1488.2352941176468
  system_state:
    active_requests: 3
    completed_requests_1min: 193
    error_rate_1min: 0.0
    avg_response_time_1min: 153.9123453624508
  metadata: {}
  efficiency:
    requests_per_second: 3.216666666666667
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 3.00
- **Baseline Value**: 0.19
- **Deviation**: 6.31 standard deviations
- **Change**: +1488.2%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 193
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 153.91ms

### Efficiency Metrics

- **Requests/sec**: 3.22
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 3.0,
    "baseline_value": 0.18888888888888888,
    "deviation": 6.30543594458351,
    "severity": "critical",
    "percentage_change": 1488.2352941176468
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 193,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 153.9123453624508
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.216666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
