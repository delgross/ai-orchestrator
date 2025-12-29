---
timestamp: 1767041481.69778
datetime: '2025-12-29T15:51:21.697780'
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
  anomaly_id: avg_response_time_1min_1767041481.69778
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 43725.484561920166
    baseline_value: 859.249271119872
    deviation: 8.787484403133233
    severity: critical
    percentage_change: 4988.8008906812465
  system_state:
    active_requests: 4
    completed_requests_1min: 5
    error_rate_1min: 0.0
    avg_response_time_1min: 43725.484561920166
  metadata: {}
  efficiency:
    requests_per_second: 0.08333333333333333
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 43725.48
- **Baseline Value**: 859.25
- **Deviation**: 8.79 standard deviations
- **Change**: +4988.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 5
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 43725.48ms

### Efficiency Metrics

- **Requests/sec**: 0.08
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
    "current_value": 43725.484561920166,
    "baseline_value": 859.249271119872,
    "deviation": 8.787484403133233,
    "severity": "critical",
    "percentage_change": 4988.8008906812465
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 5,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 43725.484561920166
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.08333333333333333,
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
