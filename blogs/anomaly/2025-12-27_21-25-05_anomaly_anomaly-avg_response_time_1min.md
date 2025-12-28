---
timestamp: 1766888705.612919
datetime: '2025-12-27T21:25:05.612919'
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
  anomaly_id: avg_response_time_1min_1766888705.612919
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 438.0060323079427
    baseline_value: 135.5701650550942
    deviation: 5.219846654503504
    severity: warning
    percentage_change: 223.0843837432387
  system_state:
    active_requests: 2
    completed_requests_1min: 75
    error_rate_1min: 0.0
    avg_response_time_1min: 438.0060323079427
  metadata: {}
  efficiency:
    requests_per_second: 1.25
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 438.01
- **Baseline Value**: 135.57
- **Deviation**: 5.22 standard deviations
- **Change**: +223.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 75
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 438.01ms

### Efficiency Metrics

- **Requests/sec**: 1.25
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
    "current_value": 438.0060323079427,
    "baseline_value": 135.5701650550942,
    "deviation": 5.219846654503504,
    "severity": "warning",
    "percentage_change": 223.0843837432387
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 75,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 438.0060323079427
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.25,
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
