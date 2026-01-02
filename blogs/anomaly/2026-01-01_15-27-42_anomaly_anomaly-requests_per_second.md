---
timestamp: 1767299262.589591
datetime: '2026-01-01T15:27:42.589591'
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
  anomaly_id: requests_per_second_1767299262.589591
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.116666666666666
    baseline_value: 2.2333333333333334
    deviation: 9.105263157894736
    severity: critical
    percentage_change: 129.1044776119403
  system_state:
    active_requests: 1
    completed_requests_1min: 307
    error_rate_1min: 0.0
    avg_response_time_1min: 122.00407873147473
  metadata: {}
  efficiency:
    requests_per_second: 5.116666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.12
- **Baseline Value**: 2.23
- **Deviation**: 9.11 standard deviations
- **Change**: +129.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 307
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 122.00ms

### Efficiency Metrics

- **Requests/sec**: 5.12
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 5.116666666666666,
    "baseline_value": 2.2333333333333334,
    "deviation": 9.105263157894736,
    "severity": "critical",
    "percentage_change": 129.1044776119403
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 307,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 122.00407873147473
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.116666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
