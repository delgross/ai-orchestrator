---
timestamp: 1767409904.7040498
datetime: '2026-01-02T22:11:44.704050'
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
  anomaly_id: avg_response_time_1min_1767409904.7040498
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 60510.11300086975
    baseline_value: 1338.8207112589191
    deviation: 44.19657672756714
    severity: critical
    percentage_change: 4419.657672756714
  system_state:
    active_requests: 2
    completed_requests_1min: 1
    error_rate_1min: 0.0
    avg_response_time_1min: 60510.11300086975
  metadata: {}
  efficiency:
    requests_per_second: 0.016666666666666666
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 60510.11
- **Baseline Value**: 1338.82
- **Deviation**: 44.20 standard deviations
- **Change**: +4419.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 1
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 60510.11ms

### Efficiency Metrics

- **Requests/sec**: 0.02
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

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
    "current_value": 60510.11300086975,
    "baseline_value": 1338.8207112589191,
    "deviation": 44.19657672756714,
    "severity": "critical",
    "percentage_change": 4419.657672756714
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 1,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 60510.11300086975
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.016666666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
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
