---
timestamp: 1766868544.347167
datetime: '2025-12-27T15:49:04.347167'
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
  anomaly_id: active_requests_1766868544.347167
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 22.0
    baseline_value: 0.923
    deviation: 52.819712622727174
    severity: critical
    percentage_change: 2283.5319609967496
  system_state:
    active_requests: 22
    completed_requests_1min: 93
    error_rate_1min: 0.0
    avg_response_time_1min: 150.72954854657573
  metadata: {}
  efficiency:
    requests_per_second: 1.55
    cache_hit_rate: 0.0
    queue_depth: 22
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 22.00
- **Baseline Value**: 0.92
- **Deviation**: 52.82 standard deviations
- **Change**: +2283.5%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 22
- **Completed Requests (1min)**: 93
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 150.73ms

### Efficiency Metrics

- **Requests/sec**: 1.55
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 22

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 22.0,
    "baseline_value": 0.923,
    "deviation": 52.819712622727174,
    "severity": "critical",
    "percentage_change": 2283.5319609967496
  },
  "system_state": {
    "active_requests": 22,
    "completed_requests_1min": 93,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 150.72954854657573
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.55,
    "cache_hit_rate": 0.0,
    "queue_depth": 22
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
