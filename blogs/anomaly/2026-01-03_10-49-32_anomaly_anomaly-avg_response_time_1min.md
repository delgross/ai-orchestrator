---
timestamp: 1767455372.87115
datetime: '2026-01-03T10:49:32.871150'
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
  anomaly_id: avg_response_time_1min_1767455372.87115
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2755.535840988159
    baseline_value: 493.9966063750418
    deviation: 15.208225235303564
    severity: critical
    percentage_change: 457.8046094705677
  system_state:
    active_requests: 0
    completed_requests_1min: 4
    error_rate_1min: 0.0
    avg_response_time_1min: 2755.535840988159
  metadata: {}
  efficiency:
    requests_per_second: 0.06666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2755.54
- **Baseline Value**: 494.00
- **Deviation**: 15.21 standard deviations
- **Change**: +457.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 4
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2755.54ms

### Efficiency Metrics

- **Requests/sec**: 0.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

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
    "current_value": 2755.535840988159,
    "baseline_value": 493.9966063750418,
    "deviation": 15.208225235303564,
    "severity": "critical",
    "percentage_change": 457.8046094705677
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 4,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2755.535840988159
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.06666666666666667,
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
3. Investigate immediately - critical system issue detected
