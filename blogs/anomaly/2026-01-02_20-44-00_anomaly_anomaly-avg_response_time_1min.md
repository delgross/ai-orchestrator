---
timestamp: 1767404640.116859
datetime: '2026-01-02T20:44:00.116859'
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
  anomaly_id: avg_response_time_1min_1767404640.116859
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 328.20402307713283
    baseline_value: 447.67144446571666
    deviation: 1.7347997701978464
    severity: warning
    percentage_change: -26.68640648526619
  system_state:
    active_requests: 1
    completed_requests_1min: 188
    error_rate_1min: 0.0
    avg_response_time_1min: 328.20402307713283
  metadata: {}
  efficiency:
    requests_per_second: 3.1333333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 328.20
- **Baseline Value**: 447.67
- **Deviation**: 1.73 standard deviations
- **Change**: -26.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 188
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 328.20ms

### Efficiency Metrics

- **Requests/sec**: 3.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 328.20402307713283,
    "baseline_value": 447.67144446571666,
    "deviation": 1.7347997701978464,
    "severity": "warning",
    "percentage_change": -26.68640648526619
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 188,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 328.20402307713283
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 3.1333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
