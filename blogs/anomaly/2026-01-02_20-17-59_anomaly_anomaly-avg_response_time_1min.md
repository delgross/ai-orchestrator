---
timestamp: 1767403079.767767
datetime: '2026-01-02T20:17:59.767767'
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
  anomaly_id: avg_response_time_1min_1767403079.767767
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 721.226667663426
    baseline_value: 505.2044129953152
    deviation: 4.124132564047969
    severity: critical
    percentage_change: 42.759376029067674
  system_state:
    active_requests: 4
    completed_requests_1min: 515
    error_rate_1min: 0.0
    avg_response_time_1min: 721.226667663426
  metadata: {}
  efficiency:
    requests_per_second: 8.583333333333334
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 721.23
- **Baseline Value**: 505.20
- **Deviation**: 4.12 standard deviations
- **Change**: +42.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 515
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 721.23ms

### Efficiency Metrics

- **Requests/sec**: 8.58
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 721.226667663426,
    "baseline_value": 505.2044129953152,
    "deviation": 4.124132564047969,
    "severity": "critical",
    "percentage_change": 42.759376029067674
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 515,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 721.226667663426
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 8.583333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
