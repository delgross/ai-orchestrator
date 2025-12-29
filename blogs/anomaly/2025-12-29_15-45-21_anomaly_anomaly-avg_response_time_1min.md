---
timestamp: 1767041121.670198
datetime: '2025-12-29T15:45:21.670198'
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
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767041121.670198
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 27867.068648338318
    baseline_value: 232.88630151642374
    deviation: 13.743724255600966
    severity: critical
    percentage_change: 11865.95440216266
  system_state:
    active_requests: 4
    completed_requests_1min: 8
    error_rate_1min: 0.0
    avg_response_time_1min: 27867.068648338318
  metadata: {}
  efficiency:
    requests_per_second: 0.13333333333333333
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 27867.07
- **Baseline Value**: 232.89
- **Deviation**: 13.74 standard deviations
- **Change**: +11866.0%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 8
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 27867.07ms

### Efficiency Metrics

- **Requests/sec**: 0.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 27867.068648338318,
    "baseline_value": 232.88630151642374,
    "deviation": 13.743724255600966,
    "severity": "critical",
    "percentage_change": 11865.95440216266
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 8,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 27867.068648338318
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.13333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance
3. Investigate immediately - critical system issue detected
