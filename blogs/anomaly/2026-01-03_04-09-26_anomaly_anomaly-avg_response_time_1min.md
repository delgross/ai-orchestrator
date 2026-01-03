---
timestamp: 1767431366.238027
datetime: '2026-01-03T04:09:26.238027'
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
- Investigate immediately - critical system issue detected
metadata:
  anomaly_id: avg_response_time_1min_1767431366.238027
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 582.576886695974
    baseline_value: 535.333512450111
    deviation: 5.438431595396246
    severity: critical
    percentage_change: 8.825035822928376
  system_state:
    active_requests: 6
    completed_requests_1min: 680
    error_rate_1min: 0.0
    avg_response_time_1min: 582.576886695974
  metadata: {}
  efficiency:
    requests_per_second: 11.333333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 582.58
- **Baseline Value**: 535.33
- **Deviation**: 5.44 standard deviations
- **Change**: +8.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 680
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 582.58ms

### Efficiency Metrics

- **Requests/sec**: 11.33
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 582.576886695974,
    "baseline_value": 535.333512450111,
    "deviation": 5.438431595396246,
    "severity": "critical",
    "percentage_change": 8.825035822928376
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 680,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 582.576886695974
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
