---
timestamp: 1766886545.487304
datetime: '2025-12-27T20:49:05.487304'
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
  anomaly_id: requests_per_second_1766886545.487304
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 1.05
    baseline_value: 2.4007166666666664
    deviation: 5.957237135122506
    severity: warning
    percentage_change: -56.263060336149614
  system_state:
    active_requests: 1
    completed_requests_1min: 63
    error_rate_1min: 0.0
    avg_response_time_1min: 122.51808529808407
  metadata: {}
  efficiency:
    requests_per_second: 1.05
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 1.05
- **Baseline Value**: 2.40
- **Deviation**: 5.96 standard deviations
- **Change**: -56.3%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 63
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 122.52ms

### Efficiency Metrics

- **Requests/sec**: 1.05
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 1.05,
    "baseline_value": 2.4007166666666664,
    "deviation": 5.957237135122506,
    "severity": "warning",
    "percentage_change": -56.263060336149614
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 63,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 122.51808529808407
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.05,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
