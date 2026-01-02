---
timestamp: 1767369031.02931
datetime: '2026-01-02T10:50:31.029310'
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
  anomaly_id: avg_response_time_1min_1767369031.02931
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 7821.81011847336
    baseline_value: 2082.1411398852742
    deviation: 6.970504408335377
    severity: critical
    percentage_change: 275.6618592582221
  system_state:
    active_requests: 10
    completed_requests_1min: 137
    error_rate_1min: 0.0
    avg_response_time_1min: 7821.81011847336
  metadata: {}
  efficiency:
    requests_per_second: 2.283333333333333
    cache_hit_rate: 0.0
    queue_depth: 10
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 7821.81
- **Baseline Value**: 2082.14
- **Deviation**: 6.97 standard deviations
- **Change**: +275.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 10
- **Completed Requests (1min)**: 137
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 7821.81ms

### Efficiency Metrics

- **Requests/sec**: 2.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 10

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
    "current_value": 7821.81011847336,
    "baseline_value": 2082.1411398852742,
    "deviation": 6.970504408335377,
    "severity": "critical",
    "percentage_change": 275.6618592582221
  },
  "system_state": {
    "active_requests": 10,
    "completed_requests_1min": 137,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 7821.81011847336
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.283333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 10
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
