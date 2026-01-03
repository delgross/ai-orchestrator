---
timestamp: 1767460895.936814
datetime: '2026-01-03T12:21:35.936814'
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
  anomaly_id: avg_response_time_1min_1767460895.936814
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 17486.150884628296
    baseline_value: 609.6525192260742
    deviation: 59.91972718085335
    severity: critical
    percentage_change: 2768.215964534381
  system_state:
    active_requests: 0
    completed_requests_1min: 5
    error_rate_1min: 0.0
    avg_response_time_1min: 17486.150884628296
  metadata: {}
  efficiency:
    requests_per_second: 0.08333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 17486.15
- **Baseline Value**: 609.65
- **Deviation**: 59.92 standard deviations
- **Change**: +2768.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 5
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 17486.15ms

### Efficiency Metrics

- **Requests/sec**: 0.08
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
    "current_value": 17486.150884628296,
    "baseline_value": 609.6525192260742,
    "deviation": 59.91972718085335,
    "severity": "critical",
    "percentage_change": 2768.215964534381
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 5,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 17486.150884628296
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.08333333333333333,
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
