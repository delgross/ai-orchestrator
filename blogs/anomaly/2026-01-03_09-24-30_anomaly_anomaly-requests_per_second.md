---
timestamp: 1767450270.217647
datetime: '2026-01-03T09:24:30.217647'
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
  anomaly_id: requests_per_second_1767450270.217647
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.533333333333333
    baseline_value: 11.133333333333333
    deviation: 2.1818181818181808
    severity: warning
    percentage_change: 3.5928143712574885
  system_state:
    active_requests: 6
    completed_requests_1min: 692
    error_rate_1min: 0.0
    avg_response_time_1min: 526.2812944505945
  metadata: {}
  efficiency:
    requests_per_second: 11.533333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.53
- **Baseline Value**: 11.13
- **Deviation**: 2.18 standard deviations
- **Change**: +3.6%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 692
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 526.28ms

### Efficiency Metrics

- **Requests/sec**: 11.53
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.533333333333333,
    "baseline_value": 11.133333333333333,
    "deviation": 2.1818181818181808,
    "severity": "warning",
    "percentage_change": 3.5928143712574885
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 692,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 526.2812944505945
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.533333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
