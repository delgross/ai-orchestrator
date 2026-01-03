---
timestamp: 1767410204.861272
datetime: '2026-01-02T22:16:44.861272'
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
  anomaly_id: avg_response_time_1min_1767410204.861272
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 22181.487262248993
    baseline_value: 1338.8207112589191
    deviation: 15.567929578405842
    severity: critical
    percentage_change: 1556.7929578405842
  system_state:
    active_requests: 2
    completed_requests_1min: 8
    error_rate_1min: 0.0
    avg_response_time_1min: 22181.487262248993
  metadata: {}
  efficiency:
    requests_per_second: 0.13333333333333333
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 22181.49
- **Baseline Value**: 1338.82
- **Deviation**: 15.57 standard deviations
- **Change**: +1556.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 8
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 22181.49ms

### Efficiency Metrics

- **Requests/sec**: 0.13
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
    "current_value": 22181.487262248993,
    "baseline_value": 1338.8207112589191,
    "deviation": 15.567929578405842,
    "severity": "critical",
    "percentage_change": 1556.7929578405842
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 8,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 22181.487262248993
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.13333333333333333,
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
