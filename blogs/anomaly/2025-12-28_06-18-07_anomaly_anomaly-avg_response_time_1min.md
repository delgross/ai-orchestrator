---
timestamp: 1766920687.98076
datetime: '2025-12-28T06:18:07.980760'
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
metadata:
  anomaly_id: avg_response_time_1min_1766920687.98076
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 245.4265321002287
    baseline_value: 29.28717180526066
    deviation: 4.265889817872332
    severity: warning
    percentage_change: 738.0001105335284
  system_state:
    active_requests: 0
    completed_requests_1min: 68
    error_rate_1min: 0.0
    avg_response_time_1min: 245.4265321002287
  metadata: {}
  efficiency:
    requests_per_second: 1.1333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 245.43
- **Baseline Value**: 29.29
- **Deviation**: 4.27 standard deviations
- **Change**: +738.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 68
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 245.43ms

### Efficiency Metrics

- **Requests/sec**: 1.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 245.4265321002287,
    "baseline_value": 29.28717180526066,
    "deviation": 4.265889817872332,
    "severity": "warning",
    "percentage_change": 738.0001105335284
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 68,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 245.4265321002287
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.1333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
