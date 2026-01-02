---
timestamp: 1767287217.203744
datetime: '2026-01-01T12:06:57.203744'
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
  anomaly_id: avg_response_time_1min_1767287217.203744
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1457.5918337878059
    baseline_value: 297.5874678655104
    deviation: 7.093014072116899
    severity: critical
    percentage_change: 389.80282813741997
  system_state:
    active_requests: 3
    completed_requests_1min: 85
    error_rate_1min: 0.0
    avg_response_time_1min: 1457.5918337878059
  metadata: {}
  efficiency:
    requests_per_second: 1.4166666666666667
    cache_hit_rate: 0.0
    queue_depth: 3
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1457.59
- **Baseline Value**: 297.59
- **Deviation**: 7.09 standard deviations
- **Change**: +389.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 3
- **Completed Requests (1min)**: 85
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1457.59ms

### Efficiency Metrics

- **Requests/sec**: 1.42
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
    "current_value": 1457.5918337878059,
    "baseline_value": 297.5874678655104,
    "deviation": 7.093014072116899,
    "severity": "critical",
    "percentage_change": 389.80282813741997
  },
  "system_state": {
    "active_requests": 3,
    "completed_requests_1min": 85,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1457.5918337878059
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.4166666666666667,
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
