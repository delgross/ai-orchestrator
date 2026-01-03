---
timestamp: 1767423169.984035
datetime: '2026-01-03T01:52:49.984035'
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
  anomaly_id: avg_response_time_1min_1767423169.984035
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 475.477891588269
    baseline_value: 434.69520655545324
    deviation: 4.105425454519074
    severity: critical
    percentage_change: 9.381903553982072
  system_state:
    active_requests: 7
    completed_requests_1min: 823
    error_rate_1min: 0.0
    avg_response_time_1min: 475.477891588269
  metadata: {}
  efficiency:
    requests_per_second: 13.716666666666667
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 475.48
- **Baseline Value**: 434.70
- **Deviation**: 4.11 standard deviations
- **Change**: +9.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 823
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 475.48ms

### Efficiency Metrics

- **Requests/sec**: 13.72
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 475.477891588269,
    "baseline_value": 434.69520655545324,
    "deviation": 4.105425454519074,
    "severity": "critical",
    "percentage_change": 9.381903553982072
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 823,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 475.477891588269
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.716666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
