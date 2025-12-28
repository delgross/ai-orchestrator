---
timestamp: 1766924228.1798022
datetime: '2025-12-28T07:17:08.179802'
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
  anomaly_id: avg_response_time_1min_1766924228.1798022
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 502.75605736356795
    baseline_value: 45.65090217287321
    deviation: 4.066654096744214
    severity: warning
    percentage_change: 1001.3058525321255
  system_state:
    active_requests: 1
    completed_requests_1min: 66
    error_rate_1min: 0.0
    avg_response_time_1min: 502.75605736356795
  metadata: {}
  efficiency:
    requests_per_second: 1.1
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 502.76
- **Baseline Value**: 45.65
- **Deviation**: 4.07 standard deviations
- **Change**: +1001.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 66
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 502.76ms

### Efficiency Metrics

- **Requests/sec**: 1.10
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
    "current_value": 502.75605736356795,
    "baseline_value": 45.65090217287321,
    "deviation": 4.066654096744214,
    "severity": "warning",
    "percentage_change": 1001.3058525321255
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 66,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 502.75605736356795
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.1,
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
