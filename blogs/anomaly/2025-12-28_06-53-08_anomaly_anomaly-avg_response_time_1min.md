---
timestamp: 1766922788.0991821
datetime: '2025-12-28T06:53:08.099182'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions:
- Check for slow upstream services or database queries
- Review recent code changes that might affect performance
metadata:
  anomaly_id: avg_response_time_1min_1766922788.0991821
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 485.69428037714073
    baseline_value: 39.448713687460135
    deviation: 4.986364952861638
    severity: warning
    percentage_change: 1131.2043536454576
  system_state:
    active_requests: 0
    completed_requests_1min: 54
    error_rate_1min: 0.0
    avg_response_time_1min: 485.69428037714073
  metadata: {}
  efficiency:
    requests_per_second: 0.9
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 485.69
- **Baseline Value**: 39.45
- **Deviation**: 4.99 standard deviations
- **Change**: +1131.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 54
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 485.69ms

### Efficiency Metrics

- **Requests/sec**: 0.90
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 485.69428037714073,
    "baseline_value": 39.448713687460135,
    "deviation": 4.986364952861638,
    "severity": "warning",
    "percentage_change": 1131.2043536454576
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 54,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 485.69428037714073
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9,
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
