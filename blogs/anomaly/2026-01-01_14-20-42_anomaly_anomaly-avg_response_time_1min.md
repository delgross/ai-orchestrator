---
timestamp: 1767295242.162425
datetime: '2026-01-01T14:20:42.162425'
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
  anomaly_id: avg_response_time_1min_1767295242.162425
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 492.71496788400117
    baseline_value: 625.6106414912659
    deviation: 3.1578419234707695
    severity: critical
    percentage_change: -21.242553242138243
  system_state:
    active_requests: 9
    completed_requests_1min: 793
    error_rate_1min: 0.0
    avg_response_time_1min: 492.71496788400117
  metadata: {}
  efficiency:
    requests_per_second: 13.216666666666667
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 492.71
- **Baseline Value**: 625.61
- **Deviation**: 3.16 standard deviations
- **Change**: -21.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 793
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 492.71ms

### Efficiency Metrics

- **Requests/sec**: 13.22
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 9

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 492.71496788400117,
    "baseline_value": 625.6106414912659,
    "deviation": 3.1578419234707695,
    "severity": "critical",
    "percentage_change": -21.242553242138243
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 793,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 492.71496788400117
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.216666666666667,
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
