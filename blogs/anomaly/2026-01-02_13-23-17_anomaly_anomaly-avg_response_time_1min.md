---
timestamp: 1767378197.881692
datetime: '2026-01-02T13:23:17.881692'
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
  anomaly_id: avg_response_time_1min_1767378197.881692
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 509.6071860477673
    baseline_value: 467.6013695693834
    deviation: 4.239494671482454
    severity: critical
    percentage_change: 8.983253517214306
  system_state:
    active_requests: 9
    completed_requests_1min: 778
    error_rate_1min: 0.0
    avg_response_time_1min: 509.6071860477673
  metadata: {}
  efficiency:
    requests_per_second: 12.966666666666667
    cache_hit_rate: 0.0
    queue_depth: 9
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 509.61
- **Baseline Value**: 467.60
- **Deviation**: 4.24 standard deviations
- **Change**: +9.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 9
- **Completed Requests (1min)**: 778
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 509.61ms

### Efficiency Metrics

- **Requests/sec**: 12.97
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
    "current_value": 509.6071860477673,
    "baseline_value": 467.6013695693834,
    "deviation": 4.239494671482454,
    "severity": "critical",
    "percentage_change": 8.983253517214306
  },
  "system_state": {
    "active_requests": 9,
    "completed_requests_1min": 778,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 509.6071860477673
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.966666666666667,
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
