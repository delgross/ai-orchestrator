---
timestamp: 1767420229.2044852
datetime: '2026-01-03T01:03:49.204485'
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
  anomaly_id: avg_response_time_1min_1767420229.2044852
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 692.2386454344756
    baseline_value: 653.7486707077907
    deviation: 4.379764604622526
    severity: critical
    percentage_change: 5.887579807238956
  system_state:
    active_requests: 29
    completed_requests_1min: 2482
    error_rate_1min: 0.0
    avg_response_time_1min: 692.2386454344756
  metadata: {}
  efficiency:
    requests_per_second: 41.36666666666667
    cache_hit_rate: 0.0
    queue_depth: 29
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 692.24
- **Baseline Value**: 653.75
- **Deviation**: 4.38 standard deviations
- **Change**: +5.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 29
- **Completed Requests (1min)**: 2482
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 692.24ms

### Efficiency Metrics

- **Requests/sec**: 41.37
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 29

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 692.2386454344756,
    "baseline_value": 653.7486707077907,
    "deviation": 4.379764604622526,
    "severity": "critical",
    "percentage_change": 5.887579807238956
  },
  "system_state": {
    "active_requests": 29,
    "completed_requests_1min": 2482,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 692.2386454344756
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 41.36666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 29
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
