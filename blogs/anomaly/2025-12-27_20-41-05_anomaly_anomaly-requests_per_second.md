---
timestamp: 1766886065.4529102
datetime: '2025-12-27T20:41:05.452910'
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
  anomaly_id: requests_per_second_1766886065.4529102
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.0
    baseline_value: 2.4387
    deviation: 35.689247667164885
    severity: critical
    percentage_change: -58.994546274654525
  system_state:
    active_requests: 1
    completed_requests_1min: 60
    error_rate_1min: 0.0
    avg_response_time_1min: 22.269773483276367
  metadata: {}
  efficiency:
    requests_per_second: 1.0
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.00
- **Baseline Value**: 2.44
- **Deviation**: 35.69 standard deviations
- **Change**: -59.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 60
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 22.27ms

### Efficiency Metrics

- **Requests/sec**: 1.00
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
    "current_value": 1.0,
    "baseline_value": 2.4387,
    "deviation": 35.689247667164885,
    "severity": "critical",
    "percentage_change": -58.994546274654525
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 60,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 22.269773483276367
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0,
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
