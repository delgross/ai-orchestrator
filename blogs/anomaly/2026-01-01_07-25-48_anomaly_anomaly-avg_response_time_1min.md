---
timestamp: 1767270348.332818
datetime: '2026-01-01T07:25:48.332818'
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
  anomaly_id: avg_response_time_1min_1767270348.332818
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 796.438973882924
    baseline_value: 319.1824289468619
    deviation: 6.1212943753454745
    severity: critical
    percentage_change: 149.52469235564237
  system_state:
    active_requests: 0
    completed_requests_1min: 69
    error_rate_1min: 0.0
    avg_response_time_1min: 796.438973882924
  metadata: {}
  efficiency:
    requests_per_second: 1.15
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 796.44
- **Baseline Value**: 319.18
- **Deviation**: 6.12 standard deviations
- **Change**: +149.5%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 69
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 796.44ms

### Efficiency Metrics

- **Requests/sec**: 1.15
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
    "current_value": 796.438973882924,
    "baseline_value": 319.1824289468619,
    "deviation": 6.1212943753454745,
    "severity": "critical",
    "percentage_change": 149.52469235564237
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 69,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 796.438973882924
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.15,
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
