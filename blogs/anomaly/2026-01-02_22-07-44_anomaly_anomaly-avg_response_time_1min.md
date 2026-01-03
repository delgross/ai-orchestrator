---
timestamp: 1767409664.6372428
datetime: '2026-01-02T22:07:44.637243'
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
  anomaly_id: avg_response_time_1min_1767409664.6372428
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 4828.934748967488
    baseline_value: 1338.8207112589191
    deviation: 2.6068569214370365
    severity: warning
    percentage_change: 260.68569214370365
  system_state:
    active_requests: 1
    completed_requests_1min: 3
    error_rate_1min: 0.0
    avg_response_time_1min: 4828.934748967488
  metadata: {}
  efficiency:
    requests_per_second: 0.05
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 4828.93
- **Baseline Value**: 1338.82
- **Deviation**: 2.61 standard deviations
- **Change**: +260.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 3
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 4828.93ms

### Efficiency Metrics

- **Requests/sec**: 0.05
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 4828.934748967488,
    "baseline_value": 1338.8207112589191,
    "deviation": 2.6068569214370365,
    "severity": "warning",
    "percentage_change": 260.68569214370365
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 3,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 4828.934748967488
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.05,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
