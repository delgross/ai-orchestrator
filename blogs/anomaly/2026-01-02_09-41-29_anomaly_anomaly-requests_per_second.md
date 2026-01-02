---
timestamp: 1767364889.932669
datetime: '2026-01-02T09:41:29.932669'
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
  anomaly_id: requests_per_second_1767364889.932669
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 7.15
    baseline_value: 0.3333333333333333
    deviation: 31.461538461538467
    severity: critical
    percentage_change: 2045.0000000000002
  system_state:
    active_requests: 10
    completed_requests_1min: 429
    error_rate_1min: 0.0
    avg_response_time_1min: 1792.2731312838469
  metadata: {}
  efficiency:
    requests_per_second: 7.15
    cache_hit_rate: 0.0
    queue_depth: 10
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 7.15
- **Baseline Value**: 0.33
- **Deviation**: 31.46 standard deviations
- **Change**: +2045.0%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 10
- **Completed Requests (1min)**: 429
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1792.27ms

### Efficiency Metrics

- **Requests/sec**: 7.15
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 10

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 7.15,
    "baseline_value": 0.3333333333333333,
    "deviation": 31.461538461538467,
    "severity": "critical",
    "percentage_change": 2045.0000000000002
  },
  "system_state": {
    "active_requests": 10,
    "completed_requests_1min": 429,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1792.2731312838469
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 7.15,
    "cache_hit_rate": 0.0,
    "queue_depth": 10
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
