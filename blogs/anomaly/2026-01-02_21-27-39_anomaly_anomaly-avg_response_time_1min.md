---
timestamp: 1767407259.048278
datetime: '2026-01-02T21:27:39.048278'
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
  anomaly_id: avg_response_time_1min_1767407259.048278
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 413.6863975590447
    baseline_value: 436.1322312668608
    deviation: 5.344297780297189
    severity: critical
    percentage_change: -5.146566132619067
  system_state:
    active_requests: 6
    completed_requests_1min: 873
    error_rate_1min: 0.0
    avg_response_time_1min: 413.6863975590447
  metadata: {}
  efficiency:
    requests_per_second: 14.55
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 413.69
- **Baseline Value**: 436.13
- **Deviation**: 5.34 standard deviations
- **Change**: -5.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 873
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 413.69ms

### Efficiency Metrics

- **Requests/sec**: 14.55
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
    "current_value": 413.6863975590447,
    "baseline_value": 436.1322312668608,
    "deviation": 5.344297780297189,
    "severity": "critical",
    "percentage_change": -5.146566132619067
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 873,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 413.6863975590447
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.55,
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
