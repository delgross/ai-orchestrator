---
timestamp: 1767291102.930512
datetime: '2026-01-01T13:11:42.930512'
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
  anomaly_id: avg_response_time_1min_1767291102.930512
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 4136.34467124939
    baseline_value: 1570.3139395653448
    deviation: 2.160949437642797
    severity: warning
    percentage_change: 163.40877241364296
  system_state:
    active_requests: 2
    completed_requests_1min: 42
    error_rate_1min: 0.0
    avg_response_time_1min: 4136.34467124939
  metadata: {}
  efficiency:
    requests_per_second: 0.7
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 4136.34
- **Baseline Value**: 1570.31
- **Deviation**: 2.16 standard deviations
- **Change**: +163.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 42
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 4136.34ms

### Efficiency Metrics

- **Requests/sec**: 0.70
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 4136.34467124939,
    "baseline_value": 1570.3139395653448,
    "deviation": 2.160949437642797,
    "severity": "warning",
    "percentage_change": 163.40877241364296
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 42,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 4136.34467124939
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.7,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
