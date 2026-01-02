---
timestamp: 1767266688.039249
datetime: '2026-01-01T06:24:48.039249'
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
  anomaly_id: avg_response_time_1min_1767266688.039249
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 835.5797579590703
    baseline_value: 333.78228040841907
    deviation: 5.785628115297982
    severity: critical
    percentage_change: 150.3367635144224
  system_state:
    active_requests: 0
    completed_requests_1min: 71
    error_rate_1min: 0.0
    avg_response_time_1min: 835.5797579590703
  metadata: {}
  efficiency:
    requests_per_second: 1.1833333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 835.58
- **Baseline Value**: 333.78
- **Deviation**: 5.79 standard deviations
- **Change**: +150.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 71
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 835.58ms

### Efficiency Metrics

- **Requests/sec**: 1.18
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
    "current_value": 835.5797579590703,
    "baseline_value": 333.78228040841907,
    "deviation": 5.785628115297982,
    "severity": "critical",
    "percentage_change": 150.3367635144224
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 71,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 835.5797579590703
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.1833333333333333,
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
