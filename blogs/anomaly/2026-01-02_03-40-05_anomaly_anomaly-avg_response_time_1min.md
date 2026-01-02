---
timestamp: 1767343205.206269
datetime: '2026-01-02T03:40:05.206269'
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
  anomaly_id: avg_response_time_1min_1767343205.206269
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 437.9206418991089
    baseline_value: 432.428272925584
    deviation: 1.5427278966088713
    severity: warning
    percentage_change: 1.2701225422580231
  system_state:
    active_requests: 6
    completed_requests_1min: 830
    error_rate_1min: 0.0
    avg_response_time_1min: 437.9206418991089
  metadata: {}
  efficiency:
    requests_per_second: 13.833333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 437.92
- **Baseline Value**: 432.43
- **Deviation**: 1.54 standard deviations
- **Change**: +1.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 830
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 437.92ms

### Efficiency Metrics

- **Requests/sec**: 13.83
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 437.9206418991089,
    "baseline_value": 432.428272925584,
    "deviation": 1.5427278966088713,
    "severity": "warning",
    "percentage_change": 1.2701225422580231
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 830,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 437.9206418991089
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.833333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
