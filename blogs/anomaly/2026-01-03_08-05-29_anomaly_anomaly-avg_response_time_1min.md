---
timestamp: 1767445529.1656692
datetime: '2026-01-03T08:05:29.165669'
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
  anomaly_id: avg_response_time_1min_1767445529.1656692
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 541.5239832048429
    baseline_value: 515.243827221959
    deviation: 2.817102414141764
    severity: warning
    percentage_change: 5.1005280596137705
  system_state:
    active_requests: 6
    completed_requests_1min: 723
    error_rate_1min: 0.0
    avg_response_time_1min: 541.5239832048429
  metadata: {}
  efficiency:
    requests_per_second: 12.05
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 541.52
- **Baseline Value**: 515.24
- **Deviation**: 2.82 standard deviations
- **Change**: +5.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 723
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 541.52ms

### Efficiency Metrics

- **Requests/sec**: 12.05
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 541.5239832048429,
    "baseline_value": 515.243827221959,
    "deviation": 2.817102414141764,
    "severity": "warning",
    "percentage_change": 5.1005280596137705
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 723,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 541.5239832048429
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.05,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
