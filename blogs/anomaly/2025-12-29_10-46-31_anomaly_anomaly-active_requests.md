---
timestamp: 1767023191.362773
datetime: '2025-12-29T10:46:31.362773'
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
  anomaly_id: active_requests_1767023191.362773
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 2.0
    baseline_value: 0.078125
    deviation: 7.13330804651255
    severity: critical
    percentage_change: 2460.0
  system_state:
    active_requests: 2
    completed_requests_1min: 220
    error_rate_1min: 0.0
    avg_response_time_1min: 220.4645872116089
  metadata: {}
  efficiency:
    requests_per_second: 3.6666666666666665
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 2.00
- **Baseline Value**: 0.08
- **Deviation**: 7.13 standard deviations
- **Change**: +2460.0%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 220
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 220.46ms

### Efficiency Metrics

- **Requests/sec**: 3.67
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 2.0,
    "baseline_value": 0.078125,
    "deviation": 7.13330804651255,
    "severity": "critical",
    "percentage_change": 2460.0
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 220,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 220.4645872116089
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.6666666666666665,
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
