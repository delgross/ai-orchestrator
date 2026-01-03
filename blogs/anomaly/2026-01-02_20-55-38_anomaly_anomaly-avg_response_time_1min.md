---
timestamp: 1767405338.7046342
datetime: '2026-01-02T20:55:38.704634'
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
  anomaly_id: avg_response_time_1min_1767405338.7046342
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1075.1469992519765
    baseline_value: 483.4021082524475
    deviation: 8.185697053935938
    severity: critical
    percentage_change: 122.41255900574217
  system_state:
    active_requests: 6
    completed_requests_1min: 356
    error_rate_1min: 0.0
    avg_response_time_1min: 1075.1469992519765
  metadata: {}
  efficiency:
    requests_per_second: 5.933333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1075.15
- **Baseline Value**: 483.40
- **Deviation**: 8.19 standard deviations
- **Change**: +122.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 356
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1075.15ms

### Efficiency Metrics

- **Requests/sec**: 5.93
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

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
    "current_value": 1075.1469992519765,
    "baseline_value": 483.4021082524475,
    "deviation": 8.185697053935938,
    "severity": "critical",
    "percentage_change": 122.41255900574217
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 356,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1075.1469992519765
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.933333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
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
