---
timestamp: 1767284817.0116322
datetime: '2026-01-01T11:26:57.011632'
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
  anomaly_id: avg_response_time_1min_1767284817.0116322
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 186.33363375792632
    baseline_value: 144.47492844349628
    deviation: 1.9759081315191043
    severity: warning
    percentage_change: 28.972989130637195
  system_state:
    active_requests: 0
    completed_requests_1min: 74
    error_rate_1min: 0.0
    avg_response_time_1min: 186.33363375792632
  metadata: {}
  efficiency:
    requests_per_second: 1.2333333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 186.33
- **Baseline Value**: 144.47
- **Deviation**: 1.98 standard deviations
- **Change**: +29.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 74
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 186.33ms

### Efficiency Metrics

- **Requests/sec**: 1.23
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 186.33363375792632,
    "baseline_value": 144.47492844349628,
    "deviation": 1.9759081315191043,
    "severity": "warning",
    "percentage_change": 28.972989130637195
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 74,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 186.33363375792632
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.2333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
