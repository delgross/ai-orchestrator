---
timestamp: 1767364049.761906
datetime: '2026-01-02T09:27:29.761906'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions:
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
- Consider increasing concurrency limits or scaling resources
metadata:
  anomaly_id: avg_response_time_1min_1767364049.761906
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 200396.08669281006
    baseline_value: 60057.64722824097
    deviation: 2.7295412793043616
    severity: warning
    percentage_change: 233.67288920132324
  system_state:
    active_requests: 12
    completed_requests_1min: 3
    error_rate_1min: 0.0
    avg_response_time_1min: 200396.08669281006
  metadata: {}
  efficiency:
    requests_per_second: 0.05
    cache_hit_rate: 0.0
    queue_depth: 12
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 200396.09
- **Baseline Value**: 60057.65
- **Deviation**: 2.73 standard deviations
- **Change**: +233.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 12
- **Completed Requests (1min)**: 3
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 200396.09ms

### Efficiency Metrics

- **Requests/sec**: 0.05
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 12

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Consider increasing concurrency limits or scaling resources


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 200396.08669281006,
    "baseline_value": 60057.64722824097,
    "deviation": 2.7295412793043616,
    "severity": "warning",
    "percentage_change": 233.67288920132324
  },
  "system_state": {
    "active_requests": 12,
    "completed_requests_1min": 3,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 200396.08669281006
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.05,
    "cache_hit_rate": 0.0,
    "queue_depth": 12
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Consider increasing concurrency limits or scaling resources
