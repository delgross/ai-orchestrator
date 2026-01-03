---
timestamp: 1767410625.009561
datetime: '2026-01-02T22:23:45.009561'
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
  anomaly_id: avg_response_time_1min_1767410625.009561
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 59311.231315135956
    baseline_value: 22181.487262248993
    deviation: 1.6739068762119766
    severity: warning
    percentage_change: 167.39068762119766
  system_state:
    active_requests: 1
    completed_requests_1min: 4
    error_rate_1min: 0.0
    avg_response_time_1min: 59311.231315135956
  metadata: {}
  efficiency:
    requests_per_second: 0.06666666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 59311.23
- **Baseline Value**: 22181.49
- **Deviation**: 1.67 standard deviations
- **Change**: +167.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 4
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 59311.23ms

### Efficiency Metrics

- **Requests/sec**: 0.07
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Check for slow upstream services or database queries
2. Review recent code changes that might affect performance


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 59311.231315135956,
    "baseline_value": 22181.487262248993,
    "deviation": 1.6739068762119766,
    "severity": "warning",
    "percentage_change": 167.39068762119766
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 4,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 59311.231315135956
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.06666666666666667,
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
