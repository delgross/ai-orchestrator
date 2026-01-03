---
timestamp: 1767421189.45755
datetime: '2026-01-03T01:19:49.457550'
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
  anomaly_id: requests_per_second_1767421189.45755
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 40.916666666666664
    baseline_value: 37.1
    deviation: 3.1805555555555447
    severity: critical
    percentage_change: 10.287511230907446
  system_state:
    active_requests: 15
    completed_requests_1min: 2455
    error_rate_1min: 0.0
    avg_response_time_1min: 347.07054897626887
  metadata: {}
  efficiency:
    requests_per_second: 40.916666666666664
    cache_hit_rate: 0.0
    queue_depth: 15
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 40.92
- **Baseline Value**: 37.10
- **Deviation**: 3.18 standard deviations
- **Change**: +10.3%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 15
- **Completed Requests (1min)**: 2455
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 347.07ms

### Efficiency Metrics

- **Requests/sec**: 40.92
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 15

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 40.916666666666664,
    "baseline_value": 37.1,
    "deviation": 3.1805555555555447,
    "severity": "critical",
    "percentage_change": 10.287511230907446
  },
  "system_state": {
    "active_requests": 15,
    "completed_requests_1min": 2455,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 347.07054897626887
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 40.916666666666664,
    "cache_hit_rate": 0.0,
    "queue_depth": 15
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
