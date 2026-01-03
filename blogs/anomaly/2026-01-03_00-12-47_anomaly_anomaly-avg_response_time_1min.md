---
timestamp: 1767417167.893332
datetime: '2026-01-03T00:12:47.893332'
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
  anomaly_id: avg_response_time_1min_1767417167.893332
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 962.8692024959142
    baseline_value: 824.5204879568952
    deviation: 20.637487404920783
    severity: critical
    percentage_change: 16.779293730085183
  system_state:
    active_requests: 31
    completed_requests_1min: 1844
    error_rate_1min: 0.0
    avg_response_time_1min: 962.8692024959142
  metadata: {}
  efficiency:
    requests_per_second: 30.733333333333334
    cache_hit_rate: 0.0
    queue_depth: 31
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 962.87
- **Baseline Value**: 824.52
- **Deviation**: 20.64 standard deviations
- **Change**: +16.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 31
- **Completed Requests (1min)**: 1844
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 962.87ms

### Efficiency Metrics

- **Requests/sec**: 30.73
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 31

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 962.8692024959142,
    "baseline_value": 824.5204879568952,
    "deviation": 20.637487404920783,
    "severity": "critical",
    "percentage_change": 16.779293730085183
  },
  "system_state": {
    "active_requests": 31,
    "completed_requests_1min": 1844,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 962.8692024959142
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 30.733333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 31
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
