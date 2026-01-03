---
timestamp: 1767409184.503587
datetime: '2026-01-02T21:59:44.503587'
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
  anomaly_id: avg_response_time_1min_1767409184.503587
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 68084.153175354
    baseline_value: 1338.8207112589191
    deviation: 49.85382426697982
    severity: critical
    percentage_change: 4985.382426697982
  system_state:
    active_requests: 0
    completed_requests_1min: 2
    error_rate_1min: 0.0
    avg_response_time_1min: 68084.153175354
  metadata: {}
  efficiency:
    requests_per_second: 0.03333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 68084.15
- **Baseline Value**: 1338.82
- **Deviation**: 49.85 standard deviations
- **Change**: +4985.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 2
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 68084.15ms

### Efficiency Metrics

- **Requests/sec**: 0.03
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
    "current_value": 68084.153175354,
    "baseline_value": 1338.8207112589191,
    "deviation": 49.85382426697982,
    "severity": "critical",
    "percentage_change": 4985.382426697982
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 2,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 68084.153175354
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.03333333333333333,
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
