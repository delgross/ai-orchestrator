---
timestamp: 1767454112.149777
datetime: '2026-01-03T10:28:32.149777'
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
  anomaly_id: avg_response_time_1min_1767454112.149777
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2587.7883183328727
    baseline_value: 487.72561065549775
    deviation: 14.718694008191362
    severity: critical
    percentage_change: 430.58282398886416
  system_state:
    active_requests: 3
    completed_requests_1min: 19
    error_rate_1min: 0.0
    avg_response_time_1min: 2587.7883183328727
  metadata: {}
  efficiency:
    requests_per_second: 0.31666666666666665
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2587.79
- **Baseline Value**: 487.73
- **Deviation**: 14.72 standard deviations
- **Change**: +430.6%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 19
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2587.79ms

### Efficiency Metrics

- **Requests/sec**: 0.32
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 3

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
    "current_value": 2587.7883183328727,
    "baseline_value": 487.72561065549775,
    "deviation": 14.718694008191362,
    "severity": "critical",
    "percentage_change": 430.58282398886416
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 19,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2587.7883183328727
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.31666666666666665,
    "cache_hit_rate": 0.0,
    "queue_depth": 3
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
