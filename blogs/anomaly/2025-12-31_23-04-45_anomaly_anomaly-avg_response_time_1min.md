---
timestamp: 1767240285.844791
datetime: '2025-12-31T23:04:45.844791'
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
  anomaly_id: avg_response_time_1min_1767240285.844791
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 523.2820766312735
    baseline_value: 180.16586380620157
    deviation: 26.616423473439173
    severity: critical
    percentage_change: 190.4446300627463
  system_state:
    active_requests: 1
    completed_requests_1min: 28
    error_rate_1min: 0.0
    avg_response_time_1min: 523.2820766312735
  metadata: {}
  efficiency:
    requests_per_second: 0.4666666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 523.28
- **Baseline Value**: 180.17
- **Deviation**: 26.62 standard deviations
- **Change**: +190.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 28
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 523.28ms

### Efficiency Metrics

- **Requests/sec**: 0.47
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
    "current_value": 523.2820766312735,
    "baseline_value": 180.16586380620157,
    "deviation": 26.616423473439173,
    "severity": "critical",
    "percentage_change": 190.4446300627463
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 28,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 523.2820766312735
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.4666666666666667,
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
