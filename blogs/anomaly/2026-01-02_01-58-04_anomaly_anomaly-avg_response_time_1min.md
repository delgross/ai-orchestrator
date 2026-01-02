---
timestamp: 1767337084.342578
datetime: '2026-01-02T01:58:04.342578'
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
  anomaly_id: avg_response_time_1min_1767337084.342578
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 416.7882800102234
    baseline_value: 423.35908187179035
    deviation: 3.68198062961786
    severity: critical
    percentage_change: -1.5520635184004057
  system_state:
    active_requests: 6
    completed_requests_1min: 868
    error_rate_1min: 0.0
    avg_response_time_1min: 416.7882800102234
  metadata: {}
  efficiency:
    requests_per_second: 14.466666666666667
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 416.79
- **Baseline Value**: 423.36
- **Deviation**: 3.68 standard deviations
- **Change**: -1.6%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 868
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 416.79ms

### Efficiency Metrics

- **Requests/sec**: 14.47
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
    "current_value": 416.7882800102234,
    "baseline_value": 423.35908187179035,
    "deviation": 3.68198062961786,
    "severity": "critical",
    "percentage_change": -1.5520635184004057
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 868,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 416.7882800102234
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.466666666666667,
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
