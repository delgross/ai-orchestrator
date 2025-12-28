---
timestamp: 1766923928.159446
datetime: '2025-12-28T07:12:08.159446'
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
  anomaly_id: avg_response_time_1min_1766923928.159446
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 807.8353014859287
    baseline_value: 43.35761357378562
    deviation: 7.2100265172349465
    severity: critical
    percentage_change: 1763.1913403424783
  system_state:
    active_requests: 0
    completed_requests_1min: 55
    error_rate_1min: 0.0
    avg_response_time_1min: 807.8353014859287
  metadata: {}
  efficiency:
    requests_per_second: 0.9166666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 807.84
- **Baseline Value**: 43.36
- **Deviation**: 7.21 standard deviations
- **Change**: +1763.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 55
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 807.84ms

### Efficiency Metrics

- **Requests/sec**: 0.92
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
    "current_value": 807.8353014859287,
    "baseline_value": 43.35761357378562,
    "deviation": 7.2100265172349465,
    "severity": "critical",
    "percentage_change": 1763.1913403424783
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 55,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 807.8353014859287
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9166666666666666,
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
