---
timestamp: 1766881925.244168
datetime: '2025-12-27T19:32:05.244168'
category: anomaly
severity: critical
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: requests_per_second_1766881925.244168
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 3.033333333333333
    baseline_value: 2.4250333333333334
    deviation: 9.211353503752164
    severity: critical
    percentage_change: 25.08419128259405
  system_state:
    active_requests: 0
    completed_requests_1min: 182
    error_rate_1min: 0.0
    avg_response_time_1min: 362.213691512307
  metadata: {}
  efficiency:
    requests_per_second: 3.033333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 3.03
- **Baseline Value**: 2.43
- **Deviation**: 9.21 standard deviations
- **Change**: +25.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 182
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 362.21ms

### Efficiency Metrics

- **Requests/sec**: 3.03
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 3.033333333333333,
    "baseline_value": 2.4250333333333334,
    "deviation": 9.211353503752164,
    "severity": "critical",
    "percentage_change": 25.08419128259405
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 182,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 362.213691512307
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.033333333333333,
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
