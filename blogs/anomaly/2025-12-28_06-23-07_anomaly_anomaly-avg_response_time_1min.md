---
timestamp: 1766920987.9968278
datetime: '2025-12-28T06:23:07.996828'
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
  anomaly_id: avg_response_time_1min_1766920987.9968278
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 379.467636346817
    baseline_value: 30.75275603254959
    deviation: 6.506564702153399
    severity: critical
    percentage_change: 1133.9305002295653
  system_state:
    active_requests: 0
    completed_requests_1min: 56
    error_rate_1min: 0.0
    avg_response_time_1min: 379.467636346817
  metadata: {}
  efficiency:
    requests_per_second: 0.9333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 379.47
- **Baseline Value**: 30.75
- **Deviation**: 6.51 standard deviations
- **Change**: +1133.9%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 56
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 379.47ms

### Efficiency Metrics

- **Requests/sec**: 0.93
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
    "current_value": 379.467636346817,
    "baseline_value": 30.75275603254959,
    "deviation": 6.506564702153399,
    "severity": "critical",
    "percentage_change": 1133.9305002295653
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 56,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 379.467636346817
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9333333333333333,
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
