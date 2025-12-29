---
timestamp: 1767041721.718339
datetime: '2025-12-29T15:55:21.718339'
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
  anomaly_id: avg_response_time_1min_1767041721.718339
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 31525.78295360912
    baseline_value: 1434.2022450463558
    deviation: 4.277412468318765
    severity: warning
    percentage_change: 2098.1406780317902
  system_state:
    active_requests: 5
    completed_requests_1min: 11
    error_rate_1min: 0.0
    avg_response_time_1min: 31525.78295360912
  metadata: {}
  efficiency:
    requests_per_second: 0.18333333333333332
    cache_hit_rate: 0.0
    queue_depth: 5
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 31525.78
- **Baseline Value**: 1434.20
- **Deviation**: 4.28 standard deviations
- **Change**: +2098.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 5
- **Completed Requests (1min)**: 11
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 31525.78ms

### Efficiency Metrics

- **Requests/sec**: 0.18
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 5

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 31525.78295360912,
    "baseline_value": 1434.2022450463558,
    "deviation": 4.277412468318765,
    "severity": "warning",
    "percentage_change": 2098.1406780317902
  },
  "system_state": {
    "active_requests": 5,
    "completed_requests_1min": 11,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 31525.78295360912
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.18333333333333332,
    "cache_hit_rate": 0.0,
    "queue_depth": 5
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
