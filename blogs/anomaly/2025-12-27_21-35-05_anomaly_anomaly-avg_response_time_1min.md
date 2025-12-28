---
timestamp: 1766889305.644973
datetime: '2025-12-27T21:35:05.644973'
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
  anomaly_id: avg_response_time_1min_1766889305.644973
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 616.7521101705144
    baseline_value: 136.17756092193852
    deviation: 7.583385221935181
    severity: critical
    percentage_change: 352.90289089849176
  system_state:
    active_requests: 2
    completed_requests_1min: 89
    error_rate_1min: 0.0
    avg_response_time_1min: 616.7521101705144
  metadata: {}
  efficiency:
    requests_per_second: 1.4833333333333334
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 616.75
- **Baseline Value**: 136.18
- **Deviation**: 7.58 standard deviations
- **Change**: +352.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 89
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 616.75ms

### Efficiency Metrics

- **Requests/sec**: 1.48
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
    "current_value": 616.7521101705144,
    "baseline_value": 136.17756092193852,
    "deviation": 7.583385221935181,
    "severity": "critical",
    "percentage_change": 352.90289089849176
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 89,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 616.7521101705144
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.4833333333333334,
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
