---
timestamp: 1767168186.871901
datetime: '2025-12-31T03:03:06.871901'
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
  anomaly_id: avg_response_time_1min_1767168186.871901
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 160.69058938459918
    baseline_value: 99.9793224647397
    deviation: 7.512964065192944
    severity: critical
    percentage_change: 60.72382310979442
  system_state:
    active_requests: 0
    completed_requests_1min: 11
    error_rate_1min: 0.0
    avg_response_time_1min: 160.69058938459918
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

- **Current Value**: 160.69
- **Baseline Value**: 99.98
- **Deviation**: 7.51 standard deviations
- **Change**: +60.7%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 11
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 160.69ms

### Efficiency Metrics

- **Requests/sec**: 0.18
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
    "current_value": 160.69058938459918,
    "baseline_value": 99.9793224647397,
    "deviation": 7.512964065192944,
    "severity": "critical",
    "percentage_change": 60.72382310979442
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 11,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 160.69058938459918
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

1. Investigate immediately - critical system issue detected
