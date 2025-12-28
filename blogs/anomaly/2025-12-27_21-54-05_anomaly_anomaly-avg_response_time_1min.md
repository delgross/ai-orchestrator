---
timestamp: 1766890445.6987782
datetime: '2025-12-27T21:54:05.698778'
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
  anomaly_id: avg_response_time_1min_1766890445.6987782
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 560.9850622713566
    baseline_value: 140.21926977403197
    deviation: 5.785316035899584
    severity: warning
    percentage_change: 300.0770102250587
  system_state:
    active_requests: 1
    completed_requests_1min: 64
    error_rate_1min: 0.0
    avg_response_time_1min: 560.9850622713566
  metadata: {}
  efficiency:
    requests_per_second: 1.0666666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 560.99
- **Baseline Value**: 140.22
- **Deviation**: 5.79 standard deviations
- **Change**: +300.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 64
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 560.99ms

### Efficiency Metrics

- **Requests/sec**: 1.07
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
    "current_value": 560.9850622713566,
    "baseline_value": 140.21926977403197,
    "deviation": 5.785316035899584,
    "severity": "warning",
    "percentage_change": 300.0770102250587
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 64,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 560.9850622713566
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0666666666666667,
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
