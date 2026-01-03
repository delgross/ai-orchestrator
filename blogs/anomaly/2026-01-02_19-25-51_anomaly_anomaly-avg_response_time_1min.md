---
timestamp: 1767399951.623151
datetime: '2026-01-02T19:25:51.623151'
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
  anomaly_id: avg_response_time_1min_1767399951.623151
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 449.11349432979955
    baseline_value: 440.1433883779465
    deviation: 1.7483318810288613
    severity: warning
    percentage_change: 2.0379962959140276
  system_state:
    active_requests: 6
    completed_requests_1min: 797
    error_rate_1min: 0.0
    avg_response_time_1min: 449.11349432979955
  metadata: {}
  efficiency:
    requests_per_second: 13.283333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 449.11
- **Baseline Value**: 440.14
- **Deviation**: 1.75 standard deviations
- **Change**: +2.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 797
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 449.11ms

### Efficiency Metrics

- **Requests/sec**: 13.28
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 449.11349432979955,
    "baseline_value": 440.1433883779465,
    "deviation": 1.7483318810288613,
    "severity": "warning",
    "percentage_change": 2.0379962959140276
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 797,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 449.11349432979955
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.283333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
