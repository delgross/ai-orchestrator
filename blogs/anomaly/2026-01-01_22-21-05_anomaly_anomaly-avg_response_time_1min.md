---
timestamp: 1767324065.726519
datetime: '2026-01-01T22:21:05.726519'
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
  anomaly_id: avg_response_time_1min_1767324065.726519
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 451.8647282981635
    baseline_value: 444.99575856871206
    deviation: 3.3352963191523703
    severity: critical
    percentage_change: 1.5436034158044278
  system_state:
    active_requests: 6
    completed_requests_1min: 803
    error_rate_1min: 0.0
    avg_response_time_1min: 451.8647282981635
  metadata: {}
  efficiency:
    requests_per_second: 13.383333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 451.86
- **Baseline Value**: 445.00
- **Deviation**: 3.34 standard deviations
- **Change**: +1.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 803
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 451.86ms

### Efficiency Metrics

- **Requests/sec**: 13.38
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 451.8647282981635,
    "baseline_value": 444.99575856871206,
    "deviation": 3.3352963191523703,
    "severity": "critical",
    "percentage_change": 1.5436034158044278
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 803,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 451.8647282981635
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.383333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
