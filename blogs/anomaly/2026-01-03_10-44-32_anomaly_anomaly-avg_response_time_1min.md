---
timestamp: 1767455072.693932
datetime: '2026-01-03T10:44:32.693932'
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
  anomaly_id: avg_response_time_1min_1767455072.693932
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1865.8784457615443
    baseline_value: 490.66686509224365
    deviation: 9.475677203438462
    severity: critical
    percentage_change: 280.2739859784022
  system_state:
    active_requests: 1
    completed_requests_1min: 14
    error_rate_1min: 0.0
    avg_response_time_1min: 1865.8784457615443
  metadata: {}
  efficiency:
    requests_per_second: 0.23333333333333334
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1865.88
- **Baseline Value**: 490.67
- **Deviation**: 9.48 standard deviations
- **Change**: +280.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 14
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1865.88ms

### Efficiency Metrics

- **Requests/sec**: 0.23
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
    "current_value": 1865.8784457615443,
    "baseline_value": 490.66686509224365,
    "deviation": 9.475677203438462,
    "severity": "critical",
    "percentage_change": 280.2739859784022
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 14,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1865.8784457615443
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.23333333333333334,
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
