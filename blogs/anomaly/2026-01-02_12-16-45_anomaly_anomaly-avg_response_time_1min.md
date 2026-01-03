---
timestamp: 1767374205.297195
datetime: '2026-01-02T12:16:45.297195'
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
  anomaly_id: avg_response_time_1min_1767374205.297195
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 834.6478063848954
    baseline_value: 699.287064479517
    deviation: 4.401693965453347
    severity: critical
    percentage_change: 19.356963510561734
  system_state:
    active_requests: 9
    completed_requests_1min: 790
    error_rate_1min: 0.0
    avg_response_time_1min: 834.6478063848954
  metadata: {}
  efficiency:
    requests_per_second: 13.166666666666666
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 834.65
- **Baseline Value**: 699.29
- **Deviation**: 4.40 standard deviations
- **Change**: +19.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 790
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 834.65ms

### Efficiency Metrics

- **Requests/sec**: 13.17
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
    "current_value": 834.6478063848954,
    "baseline_value": 699.287064479517,
    "deviation": 4.401693965453347,
    "severity": "critical",
    "percentage_change": 19.356963510561734
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 790,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 834.6478063848954
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.166666666666666,
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
