---
timestamp: 1767457834.26288
datetime: '2026-01-03T11:30:34.262880'
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
  anomaly_id: avg_response_time_1min_1767457834.26288
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 3062.9383087158203
    baseline_value: 499.12360191345215
    deviation: 15.835352894501971
    severity: critical
    percentage_change: 513.6632884066526
  system_state:
    active_requests: 0
    completed_requests_1min: 5
    error_rate_1min: 0.0
    avg_response_time_1min: 3062.9383087158203
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

- **Current Value**: 3062.94
- **Baseline Value**: 499.12
- **Deviation**: 15.84 standard deviations
- **Change**: +513.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 5
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 3062.94ms

### Efficiency Metrics

- **Requests/sec**: 0.08
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
    "current_value": 3062.9383087158203,
    "baseline_value": 499.12360191345215,
    "deviation": 15.835352894501971,
    "severity": "critical",
    "percentage_change": 513.6632884066526
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 5,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 3062.9383087158203
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
3. Investigate immediately - critical system issue detected
