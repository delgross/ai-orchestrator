---
timestamp: 1767435567.1051252
datetime: '2026-01-03T05:19:27.105125'
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
  anomaly_id: requests_per_second_1767435567.1051252
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 10.916666666666666
    baseline_value: 11.1
    deviation: 1.5714285714285672
    severity: warning
    percentage_change: -1.651651651651654
  system_state:
    active_requests: 6
    completed_requests_1min: 655
    error_rate_1min: 0.0
    avg_response_time_1min: 547.7625046067566
  metadata: {}
  efficiency:
    requests_per_second: 10.916666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 10.92
- **Baseline Value**: 11.10
- **Deviation**: 1.57 standard deviations
- **Change**: -1.7%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 655
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 547.76ms

### Efficiency Metrics

- **Requests/sec**: 10.92
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 10.916666666666666,
    "baseline_value": 11.1,
    "deviation": 1.5714285714285672,
    "severity": "warning",
    "percentage_change": -1.651651651651654
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 655,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 547.7625046067566
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.916666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
