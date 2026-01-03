---
timestamp: 1767458734.8031418
datetime: '2026-01-03T11:45:34.803142'
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
  anomaly_id: avg_response_time_1min_1767458734.8031418
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2115.448440824236
    baseline_value: 547.5216222232616
    deviation: 7.319698257617857
    severity: critical
    percentage_change: 286.36801816780576
  system_state:
    active_requests: 2
    completed_requests_1min: 7
    error_rate_1min: 0.0
    avg_response_time_1min: 2115.448440824236
  metadata: {}
  efficiency:
    requests_per_second: 0.11666666666666667
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2115.45
- **Baseline Value**: 547.52
- **Deviation**: 7.32 standard deviations
- **Change**: +286.4%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 7
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2115.45ms

### Efficiency Metrics

- **Requests/sec**: 0.12
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
    "current_value": 2115.448440824236,
    "baseline_value": 547.5216222232616,
    "deviation": 7.319698257617857,
    "severity": "critical",
    "percentage_change": 286.36801816780576
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 7,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2115.448440824236
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.11666666666666667,
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
