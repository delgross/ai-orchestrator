---
timestamp: 1767395330.596906
datetime: '2026-01-02T18:08:50.596906'
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
  anomaly_id: avg_response_time_1min_1767395330.596906
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 466.11817027326157
    baseline_value: 489.82203219365
    deviation: 3.468370296948678
    severity: critical
    percentage_change: -4.839280465648216
  system_state:
    active_requests: 6
    completed_requests_1min: 843
    error_rate_1min: 0.0
    avg_response_time_1min: 466.11817027326157
  metadata: {}
  efficiency:
    requests_per_second: 14.05
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 466.12
- **Baseline Value**: 489.82
- **Deviation**: 3.47 standard deviations
- **Change**: -4.8%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 843
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 466.12ms

### Efficiency Metrics

- **Requests/sec**: 14.05
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
    "current_value": 466.11817027326157,
    "baseline_value": 489.82203219365,
    "deviation": 3.468370296948678,
    "severity": "critical",
    "percentage_change": -4.839280465648216
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 843,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 466.11817027326157
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.05,
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
