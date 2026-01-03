---
timestamp: 1767453811.987808
datetime: '2026-01-03T10:23:31.987808'
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
  anomaly_id: avg_response_time_1min_1767453811.987808
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 4247.240096330643
    baseline_value: 486.63849407626736
    deviation: 26.430395011603654
    severity: critical
    percentage_change: 772.7710914839802
  system_state:
    active_requests: 0
    completed_requests_1min: 8
    error_rate_1min: 0.0
    avg_response_time_1min: 4247.240096330643
  metadata: {}
  efficiency:
    requests_per_second: 0.13333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 4247.24
- **Baseline Value**: 486.64
- **Deviation**: 26.43 standard deviations
- **Change**: +772.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 8
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 4247.24ms

### Efficiency Metrics

- **Requests/sec**: 0.13
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
    "current_value": 4247.240096330643,
    "baseline_value": 486.63849407626736,
    "deviation": 26.430395011603654,
    "severity": "critical",
    "percentage_change": 772.7710914839802
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 8,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 4247.240096330643
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.13333333333333333,
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
