---
timestamp: 1767402659.66047
datetime: '2026-01-02T20:10:59.660470'
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
  anomaly_id: avg_response_time_1min_1767402659.66047
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 510.6839009818148
    baseline_value: 444.3028585218076
    deviation: 11.165471752899892
    severity: critical
    percentage_change: 14.940494121702585
  system_state:
    active_requests: 2
    completed_requests_1min: 821
    error_rate_1min: 0.0
    avg_response_time_1min: 510.6839009818148
  metadata: {}
  efficiency:
    requests_per_second: 13.683333333333334
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 510.68
- **Baseline Value**: 444.30
- **Deviation**: 11.17 standard deviations
- **Change**: +14.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 821
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 510.68ms

### Efficiency Metrics

- **Requests/sec**: 13.68
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 510.6839009818148,
    "baseline_value": 444.3028585218076,
    "deviation": 11.165471752899892,
    "severity": "critical",
    "percentage_change": 14.940494121702585
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 821,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 510.6839009818148
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.683333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
