---
timestamp: 1767299922.6613371
datetime: '2026-01-01T15:38:42.661337'
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
  anomaly_id: avg_response_time_1min_1767299922.6613371
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 5409.886971116066
    baseline_value: 1307.9713370118823
    deviation: 5.037318218454694
    severity: critical
    percentage_change: 313.60898500078673
  system_state:
    active_requests: 1
    completed_requests_1min: 16
    error_rate_1min: 0.0
    avg_response_time_1min: 5409.886971116066
  metadata: {}
  efficiency:
    requests_per_second: 0.26666666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 5409.89
- **Baseline Value**: 1307.97
- **Deviation**: 5.04 standard deviations
- **Change**: +313.6%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 16
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 5409.89ms

### Efficiency Metrics

- **Requests/sec**: 0.27
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
    "current_value": 5409.886971116066,
    "baseline_value": 1307.9713370118823,
    "deviation": 5.037318218454694,
    "severity": "critical",
    "percentage_change": 313.60898500078673
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 16,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 5409.886971116066
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.26666666666666666,
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
