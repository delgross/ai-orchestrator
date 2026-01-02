---
timestamp: 1767292985.315163
datetime: '2026-01-01T13:43:05.315163'
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
  anomaly_id: avg_response_time_1min_1767292985.315163
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 359.1014482442615
    baseline_value: 209.85250533381594
    deviation: 4.337421229020564
    severity: critical
    percentage_change: 71.12087733860159
  system_state:
    active_requests: 0
    completed_requests_1min: 103
    error_rate_1min: 0.0
    avg_response_time_1min: 359.1014482442615
  metadata: {}
  efficiency:
    requests_per_second: 1.7166666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 359.10
- **Baseline Value**: 209.85
- **Deviation**: 4.34 standard deviations
- **Change**: +71.1%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 103
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 359.10ms

### Efficiency Metrics

- **Requests/sec**: 1.72
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 359.1014482442615,
    "baseline_value": 209.85250533381594,
    "deviation": 4.337421229020564,
    "severity": "critical",
    "percentage_change": 71.12087733860159
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 103,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 359.1014482442615
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.7166666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
