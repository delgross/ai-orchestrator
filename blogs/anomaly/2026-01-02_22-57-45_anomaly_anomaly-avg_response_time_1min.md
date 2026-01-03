---
timestamp: 1767412665.250278
datetime: '2026-01-02T22:57:45.250278'
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
  anomaly_id: avg_response_time_1min_1767412665.250278
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 86122.10893630981
    baseline_value: 33030.508041381836
    deviation: 1.620268204318858
    severity: warning
    percentage_change: 160.7350417632477
  system_state:
    active_requests: 0
    completed_requests_1min: 1
    error_rate_1min: 0.0
    avg_response_time_1min: 86122.10893630981
  metadata: {}
  efficiency:
    requests_per_second: 0.016666666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 86122.11
- **Baseline Value**: 33030.51
- **Deviation**: 1.62 standard deviations
- **Change**: +160.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 1
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 86122.11ms

### Efficiency Metrics

- **Requests/sec**: 0.02
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
    "current_value": 86122.10893630981,
    "baseline_value": 33030.508041381836,
    "deviation": 1.620268204318858,
    "severity": "warning",
    "percentage_change": 160.7350417632477
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 1,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 86122.10893630981
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.016666666666666666,
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
