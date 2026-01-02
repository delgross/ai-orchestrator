---
timestamp: 1767286564.9654698
datetime: '2026-01-01T11:56:04.965470'
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
  anomaly_id: avg_response_time_1min_1767286564.9654698
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2571.010735630989
    baseline_value: 271.36449363287977
    deviation: 20.546859809748796
    severity: critical
    percentage_change: 847.438149041424
  system_state:
    active_requests: 4
    completed_requests_1min: 80
    error_rate_1min: 0.0
    avg_response_time_1min: 2571.010735630989
  metadata: {}
  efficiency:
    requests_per_second: 1.3333333333333333
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2571.01
- **Baseline Value**: 271.36
- **Deviation**: 20.55 standard deviations
- **Change**: +847.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 80
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2571.01ms

### Efficiency Metrics

- **Requests/sec**: 1.33
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
    "current_value": 2571.010735630989,
    "baseline_value": 271.36449363287977,
    "deviation": 20.546859809748796,
    "severity": "critical",
    "percentage_change": 847.438149041424
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 80,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2571.010735630989
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.3333333333333333,
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
