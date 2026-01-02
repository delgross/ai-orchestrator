---
timestamp: 1767283953.728686
datetime: '2026-01-01T11:12:33.728686'
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
  anomaly_id: avg_response_time_1min_1767283953.728686
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1241.3164377212524
    baseline_value: 521.7098295688629
    deviation: 2.552332383579065
    severity: warning
    percentage_change: 137.9323461754721
  system_state:
    active_requests: 0
    completed_requests_1min: 16
    error_rate_1min: 0.0
    avg_response_time_1min: 1241.3164377212524
  metadata: {}
  efficiency:
    requests_per_second: 0.26666666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1241.32
- **Baseline Value**: 521.71
- **Deviation**: 2.55 standard deviations
- **Change**: +137.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 16
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1241.32ms

### Efficiency Metrics

- **Requests/sec**: 0.27
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
    "current_value": 1241.3164377212524,
    "baseline_value": 521.7098295688629,
    "deviation": 2.552332383579065,
    "severity": "warning",
    "percentage_change": 137.9323461754721
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 16,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1241.3164377212524
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.26666666666666666,
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
