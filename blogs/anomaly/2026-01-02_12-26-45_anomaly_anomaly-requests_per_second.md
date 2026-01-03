---
timestamp: 1767374805.414953
datetime: '2026-01-02T12:26:45.414953'
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
  anomaly_id: requests_per_second_1767374805.414953
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.85
    baseline_value: 13.3
    deviation: 4.124999999999952
    severity: critical
    percentage_change: 4.135338345864653
  system_state:
    active_requests: 9
    completed_requests_1min: 831
    error_rate_1min: 0.0
    avg_response_time_1min: 837.9883261220407
  metadata: {}
  efficiency:
    requests_per_second: 13.85
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.85
- **Baseline Value**: 13.30
- **Deviation**: 4.12 standard deviations
- **Change**: +4.1%
- **Severity**: CRITICAL

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 831
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 837.99ms

### Efficiency Metrics

- **Requests/sec**: 13.85
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.85,
    "baseline_value": 13.3,
    "deviation": 4.124999999999952,
    "severity": "critical",
    "percentage_change": 4.135338345864653
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 831,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 837.9883261220407
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.85,
    "cache_hit_rate": 0.0,
    "queue_depth": 9
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
