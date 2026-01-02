---
timestamp: 1767333963.957362
datetime: '2026-01-02T01:06:03.957362'
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
  anomaly_id: avg_response_time_1min_1767333963.957362
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2111.9733651479087
    baseline_value: 1084.476661682129
    deviation: 3.8317533490089977
    severity: critical
    percentage_change: 94.74585666712572
  system_state:
    active_requests: 0
    completed_requests_1min: 9
    error_rate_1min: 0.0
    avg_response_time_1min: 2111.9733651479087
  metadata: {}
  efficiency:
    requests_per_second: 0.15
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2111.97
- **Baseline Value**: 1084.48
- **Deviation**: 3.83 standard deviations
- **Change**: +94.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 9
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2111.97ms

### Efficiency Metrics

- **Requests/sec**: 0.15
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 2111.9733651479087,
    "baseline_value": 1084.476661682129,
    "deviation": 3.8317533490089977,
    "severity": "critical",
    "percentage_change": 94.74585666712572
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 9,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2111.9733651479087
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.15,
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
