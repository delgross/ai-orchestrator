---
timestamp: 1767191295.5120351
datetime: '2025-12-31T09:28:15.512035'
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
  anomaly_id: avg_response_time_1min_1767191295.5120351
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 144.07384768128395
    baseline_value: 103.52323576807976
    deviation: 3.914756785634844
    severity: critical
    percentage_change: 39.17054138845564
  system_state:
    active_requests: 0
    completed_requests_1min: 64
    error_rate_1min: 0.0
    avg_response_time_1min: 144.07384768128395
  metadata: {}
  efficiency:
    requests_per_second: 1.0666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 144.07
- **Baseline Value**: 103.52
- **Deviation**: 3.91 standard deviations
- **Change**: +39.2%
- **Severity**: CRITICAL

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 64
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 144.07ms

### Efficiency Metrics

- **Requests/sec**: 1.07
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
    "current_value": 144.07384768128395,
    "baseline_value": 103.52323576807976,
    "deviation": 3.914756785634844,
    "severity": "critical",
    "percentage_change": 39.17054138845564
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 64,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 144.07384768128395
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.0666666666666667,
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
