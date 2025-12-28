---
timestamp: 1766926388.29245
datetime: '2025-12-28T07:53:08.292450'
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
  anomaly_id: requests_per_second_1766926388.29245
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.5333333333333333
    baseline_value: 0.9271833333333334
    deviation: 6.6829627282334325
    severity: critical
    percentage_change: -42.47811472020996
  system_state:
    active_requests: 0
    completed_requests_1min: 32
    error_rate_1min: 0.0
    avg_response_time_1min: 4.580475389957428
  metadata: {}
  efficiency:
    requests_per_second: 0.5333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.53
- **Baseline Value**: 0.93
- **Deviation**: 6.68 standard deviations
- **Change**: -42.5%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 32
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 4.58ms

### Efficiency Metrics

- **Requests/sec**: 0.53
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
    "current_value": 0.5333333333333333,
    "baseline_value": 0.9271833333333334,
    "deviation": 6.6829627282334325,
    "severity": "critical",
    "percentage_change": -42.47811472020996
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 32,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 4.580475389957428
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.5333333333333333,
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
