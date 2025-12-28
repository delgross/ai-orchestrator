---
timestamp: 1766945211.3757892
datetime: '2025-12-28T13:06:51.375789'
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
  anomaly_id: avg_response_time_1min_1766945211.3757892
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1004.3932437896729
    baseline_value: 96.34609969090869
    deviation: 4.733519751806861
    severity: warning
    percentage_change: 942.4845915007481
  system_state:
    active_requests: 0
    completed_requests_1min: 5
    error_rate_1min: 0.0
    avg_response_time_1min: 1004.3932437896729
  metadata: {}
  efficiency:
    requests_per_second: 0.08333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1004.39
- **Baseline Value**: 96.35
- **Deviation**: 4.73 standard deviations
- **Change**: +942.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 5
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1004.39ms

### Efficiency Metrics

- **Requests/sec**: 0.08
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
    "current_value": 1004.3932437896729,
    "baseline_value": 96.34609969090869,
    "deviation": 4.733519751806861,
    "severity": "warning",
    "percentage_change": 942.4845915007481
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 5,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1004.3932437896729
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.08333333333333333,
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
