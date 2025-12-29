---
timestamp: 1766981994.276932
datetime: '2025-12-28T23:19:54.276932'
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
  anomaly_id: avg_response_time_1min_1766981994.276932
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 244.0570302911707
    baseline_value: 151.26189268329006
    deviation: 7.277476039680407
    severity: critical
    percentage_change: 61.34733339756215
  system_state:
    active_requests: 1
    completed_requests_1min: 111
    error_rate_1min: 0.0
    avg_response_time_1min: 244.0570302911707
  metadata: {}
  efficiency:
    requests_per_second: 1.85
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 244.06
- **Baseline Value**: 151.26
- **Deviation**: 7.28 standard deviations
- **Change**: +61.3%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 111
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 244.06ms

### Efficiency Metrics

- **Requests/sec**: 1.85
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage


## Suggested Actions

1. Investigate immediately - critical system issue detected


## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 244.0570302911707,
    "baseline_value": 151.26189268329006,
    "deviation": 7.277476039680407,
    "severity": "critical",
    "percentage_change": 61.34733339756215
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 111,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 244.0570302911707
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.85,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```

## Suggested Actions

1. Investigate immediately - critical system issue detected
