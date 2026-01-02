---
timestamp: 1767317291.070684
datetime: '2026-01-01T20:28:11.070684'
category: anomaly
severity: critical
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- critical
resolution_status: open
suggested_actions:
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767317291.070684
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 299.1376632735843
    baseline_value: 205.0165891647339
    deviation: 10.127899118055275
    severity: critical
    percentage_change: 45.90900399441467
  system_state:
    active_requests: 1
    completed_requests_1min: 252
    error_rate_1min: 0.0
    avg_response_time_1min: 299.1376632735843
  metadata: {}
  efficiency:
    requests_per_second: 4.2
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 299.14
- **Baseline Value**: 205.02
- **Deviation**: 10.13 standard deviations
- **Change**: +45.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 252
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 299.14ms

### Efficiency Metrics

- **Requests/sec**: 4.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 299.1376632735843,
    "baseline_value": 205.0165891647339,
    "deviation": 10.127899118055275,
    "severity": "critical",
    "percentage_change": 45.90900399441467
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 252,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 299.1376632735843
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 4.2,
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
