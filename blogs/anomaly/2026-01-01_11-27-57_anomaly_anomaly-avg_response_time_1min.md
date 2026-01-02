---
timestamp: 1767284877.019417
datetime: '2026-01-01T11:27:57.019417'
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
  anomaly_id: avg_response_time_1min_1767284877.019417
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 464.0961236591581
    baseline_value: 144.47492844349628
    deviation: 15.08747377369955
    severity: critical
    percentage_change: 221.2295231145691
  system_state:
    active_requests: 0
    completed_requests_1min: 79
    error_rate_1min: 0.0
    avg_response_time_1min: 464.0961236591581
  metadata: {}
  efficiency:
    requests_per_second: 1.3166666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 464.10
- **Baseline Value**: 144.47
- **Deviation**: 15.09 standard deviations
- **Change**: +221.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 79
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 464.10ms

### Efficiency Metrics

- **Requests/sec**: 1.32
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
    "current_value": 464.0961236591581,
    "baseline_value": 144.47492844349628,
    "deviation": 15.08747377369955,
    "severity": "critical",
    "percentage_change": 221.2295231145691
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 79,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 464.0961236591581
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.3166666666666667,
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
