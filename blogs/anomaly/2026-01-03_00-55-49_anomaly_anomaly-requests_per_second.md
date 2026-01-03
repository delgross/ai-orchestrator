---
timestamp: 1767419749.0737522
datetime: '2026-01-03T00:55:49.073752'
category: anomaly
severity: warning
title: 'Anomaly: requests_per_second'
source: anomaly_detector
tags:
- anomaly
- requests_per_second
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: requests_per_second_1767419749.0737522
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 28.65
    baseline_value: 34.016666666666666
    deviation: 2.66115702479339
    severity: warning
    percentage_change: -15.7765801077903
  system_state:
    active_requests: 30
    completed_requests_1min: 1719
    error_rate_1min: 0.0
    avg_response_time_1min: 1041.004718632945
  metadata: {}
  efficiency:
    requests_per_second: 28.65
    cache_hit_rate: 0.0
    queue_depth: 30
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 28.65
- **Baseline Value**: 34.02
- **Deviation**: 2.66 standard deviations
- **Change**: -15.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 30
- **Completed Requests (1min)**: 1719
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1041.00ms

### Efficiency Metrics

- **Requests/sec**: 28.65
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 30

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 28.65,
    "baseline_value": 34.016666666666666,
    "deviation": 2.66115702479339,
    "severity": "warning",
    "percentage_change": -15.7765801077903
  },
  "system_state": {
    "active_requests": 30,
    "completed_requests_1min": 1719,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1041.004718632945
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 28.65,
    "cache_hit_rate": 0.0,
    "queue_depth": 30
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
