---
timestamp: 1767451410.56882
datetime: '2026-01-03T09:43:30.568820'
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
  anomaly_id: avg_response_time_1min_1767451410.56882
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1608.9785993099213
    baseline_value: 472.33500138172127
    deviation: 8.834288885442248
    severity: critical
    percentage_change: 240.6435251681915
  system_state:
    active_requests: 1
    completed_requests_1min: 8
    error_rate_1min: 0.0
    avg_response_time_1min: 1608.9785993099213
  metadata: {}
  efficiency:
    requests_per_second: 0.13333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1608.98
- **Baseline Value**: 472.34
- **Deviation**: 8.83 standard deviations
- **Change**: +240.6%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 8
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1608.98ms

### Efficiency Metrics

- **Requests/sec**: 0.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

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
    "current_value": 1608.9785993099213,
    "baseline_value": 472.33500138172127,
    "deviation": 8.834288885442248,
    "severity": "critical",
    "percentage_change": 240.6435251681915
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 8,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1608.9785993099213
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.13333333333333333,
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
3. Investigate immediately - critical system issue detected
