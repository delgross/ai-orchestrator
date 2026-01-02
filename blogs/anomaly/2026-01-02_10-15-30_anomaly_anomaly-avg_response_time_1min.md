---
timestamp: 1767366930.5382679
datetime: '2026-01-02T10:15:30.538268'
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
  anomaly_id: avg_response_time_1min_1767366930.5382679
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 470.59700566919605
    baseline_value: 861.0984971208021
    deviation: 2.846063961533762
    severity: warning
    percentage_change: -45.34922459594343
  system_state:
    active_requests: 16
    completed_requests_1min: 796
    error_rate_1min: 0.0
    avg_response_time_1min: 470.59700566919605
  metadata: {}
  efficiency:
    requests_per_second: 13.266666666666667
    cache_hit_rate: 0.0
    queue_depth: 16
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 470.60
- **Baseline Value**: 861.10
- **Deviation**: 2.85 standard deviations
- **Change**: -45.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 16
- **Completed Requests (1min)**: 796
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 470.60ms

### Efficiency Metrics

- **Requests/sec**: 13.27
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 16

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 470.59700566919605,
    "baseline_value": 861.0984971208021,
    "deviation": 2.846063961533762,
    "severity": "warning",
    "percentage_change": -45.34922459594343
  },
  "system_state": {
    "active_requests": 16,
    "completed_requests_1min": 796,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 470.59700566919605
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.266666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 16
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
