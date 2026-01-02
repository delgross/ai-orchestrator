---
timestamp: 1767240885.894814
datetime: '2025-12-31T23:14:45.894814'
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
  anomaly_id: avg_response_time_1min_1767240885.894814
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2239.0296611380068
    baseline_value: 181.91611766815186
    deviation: 151.56792950619328
    severity: critical
    percentage_change: 1130.8033448814056
  system_state:
    active_requests: 1
    completed_requests_1min: 94
    error_rate_1min: 0.0
    avg_response_time_1min: 2239.0296611380068
  metadata: {}
  efficiency:
    requests_per_second: 1.5666666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2239.03
- **Baseline Value**: 181.92
- **Deviation**: 151.57 standard deviations
- **Change**: +1130.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 94
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2239.03ms

### Efficiency Metrics

- **Requests/sec**: 1.57
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
    "current_value": 2239.0296611380068,
    "baseline_value": 181.91611766815186,
    "deviation": 151.56792950619328,
    "severity": "critical",
    "percentage_change": 1130.8033448814056
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 94,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2239.0296611380068
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.5666666666666667,
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
