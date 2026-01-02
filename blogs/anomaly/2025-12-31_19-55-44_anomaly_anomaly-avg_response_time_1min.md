---
timestamp: 1767228944.982661
datetime: '2025-12-31T19:55:44.982661'
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
  anomaly_id: avg_response_time_1min_1767228944.982661
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 546.8348477567945
    baseline_value: 190.69042513447422
    deviation: 12.067807859432726
    severity: critical
    percentage_change: 186.7657604576467
  system_state:
    active_requests: 1
    completed_requests_1min: 56
    error_rate_1min: 0.0
    avg_response_time_1min: 546.8348477567945
  metadata: {}
  efficiency:
    requests_per_second: 0.9333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 546.83
- **Baseline Value**: 190.69
- **Deviation**: 12.07 standard deviations
- **Change**: +186.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 56
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 546.83ms

### Efficiency Metrics

- **Requests/sec**: 0.93
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
    "current_value": 546.8348477567945,
    "baseline_value": 190.69042513447422,
    "deviation": 12.067807859432726,
    "severity": "critical",
    "percentage_change": 186.7657604576467
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 56,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 546.8348477567945
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9333333333333333,
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
