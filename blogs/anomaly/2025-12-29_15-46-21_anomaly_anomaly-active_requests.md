---
timestamp: 1767041181.675864
datetime: '2025-12-29T15:46:21.675864'
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
  anomaly_id: active_requests_1767041181.675864
structured_data:
  anomaly:
    metric_name: active_requests
    current_value: 4.0
    baseline_value: 0.07482993197278912
    deviation: 7.410045313911306
    severity: critical
    percentage_change: 5245.454545454545
  system_state:
    active_requests: 4
    completed_requests_1min: 8
    error_rate_1min: 0.0
    avg_response_time_1min: 27496.16366624832
  metadata: {}
  efficiency:
    requests_per_second: 0.13333333333333333
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: active_requests

An anomaly was detected in the **active_requests** metric.

## Details

- **Current Value**: 4.00
- **Baseline Value**: 0.07
- **Deviation**: 7.41 standard deviations
- **Change**: +5245.5%
- **Severity**: CRITICAL

**What this means**: Number of currently active requests. High values may indicate system overload.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 8
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 27496.16ms

### Efficiency Metrics

- **Requests/sec**: 0.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "active_requests",
    "current_value": 4.0,
    "baseline_value": 0.07482993197278912,
    "deviation": 7.410045313911306,
    "severity": "critical",
    "percentage_change": 5245.454545454545
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 8,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 27496.16366624832
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.13333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
