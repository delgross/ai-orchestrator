---
timestamp: 1767356610.755126
datetime: '2026-01-02T07:23:30.755126'
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
  anomaly_id: avg_response_time_1min_1767356610.755126
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 8817.975034316381
    baseline_value: 814.1743334683966
    deviation: 57.33651773868971
    severity: critical
    percentage_change: 983.0573590734131
  system_state:
    active_requests: 4
    completed_requests_1min: 24
    error_rate_1min: 0.0
    avg_response_time_1min: 8817.975034316381
  metadata: {}
  efficiency:
    requests_per_second: 0.4
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 8817.98
- **Baseline Value**: 814.17
- **Deviation**: 57.34 standard deviations
- **Change**: +983.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 24
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 8817.98ms

### Efficiency Metrics

- **Requests/sec**: 0.40
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
    "current_value": 8817.975034316381,
    "baseline_value": 814.1743334683966,
    "deviation": 57.33651773868971,
    "severity": "critical",
    "percentage_change": 983.0573590734131
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 24,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 8817.975034316381
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.4,
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
