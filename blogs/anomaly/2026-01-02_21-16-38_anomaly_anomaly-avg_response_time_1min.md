---
timestamp: 1767406598.913721
datetime: '2026-01-02T21:16:38.913721'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: avg_response_time_1min_1767406598.913721
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 621.3632607460022
    baseline_value: 440.5863506115036
    deviation: 2.8807121565857594
    severity: warning
    percentage_change: 41.030982889867715
  system_state:
    active_requests: 2
    completed_requests_1min: 200
    error_rate_1min: 0.0
    avg_response_time_1min: 621.3632607460022
  metadata: {}
  efficiency:
    requests_per_second: 3.3333333333333335
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 621.36
- **Baseline Value**: 440.59
- **Deviation**: 2.88 standard deviations
- **Change**: +41.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 200
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 621.36ms

### Efficiency Metrics

- **Requests/sec**: 3.33
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 621.3632607460022,
    "baseline_value": 440.5863506115036,
    "deviation": 2.8807121565857594,
    "severity": "warning",
    "percentage_change": 41.030982889867715
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 200,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 621.3632607460022
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.3333333333333335,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
