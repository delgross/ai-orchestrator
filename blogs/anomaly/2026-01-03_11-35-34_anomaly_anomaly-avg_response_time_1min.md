---
timestamp: 1767458134.471318
datetime: '2026-01-03T11:35:34.471318'
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
  anomaly_id: avg_response_time_1min_1767458134.471318
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 2613.9777356928043
    baseline_value: 503.8231201171875
    deviation: 12.577180476132702
    severity: critical
    percentage_change: 418.82846009226455
  system_state:
    active_requests: 0
    completed_requests_1min: 11
    error_rate_1min: 0.0
    avg_response_time_1min: 2613.9777356928043
  metadata: {}
  efficiency:
    requests_per_second: 0.18333333333333332
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 2613.98
- **Baseline Value**: 503.82
- **Deviation**: 12.58 standard deviations
- **Change**: +418.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 11
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 2613.98ms

### Efficiency Metrics

- **Requests/sec**: 0.18
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
    "current_value": 2613.9777356928043,
    "baseline_value": 503.8231201171875,
    "deviation": 12.577180476132702,
    "severity": "critical",
    "percentage_change": 418.82846009226455
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 11,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 2613.9777356928043
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.18333333333333332,
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
