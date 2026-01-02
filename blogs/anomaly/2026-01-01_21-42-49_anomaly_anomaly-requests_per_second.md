---
timestamp: 1767321769.370878
datetime: '2026-01-01T21:42:49.370878'
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
  anomaly_id: requests_per_second_1767321769.370878
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.5
    baseline_value: 12.983333333333333
    deviation: 1.8235294117647096
    severity: warning
    percentage_change: 3.979460847240058
  system_state:
    active_requests: 6
    completed_requests_1min: 810
    error_rate_1min: 0.0
    avg_response_time_1min: 445.0908716814018
  metadata: {}
  efficiency:
    requests_per_second: 13.5
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.50
- **Baseline Value**: 12.98
- **Deviation**: 1.82 standard deviations
- **Change**: +4.0%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 810
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 445.09ms

### Efficiency Metrics

- **Requests/sec**: 13.50
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.5,
    "baseline_value": 12.983333333333333,
    "deviation": 1.8235294117647096,
    "severity": "warning",
    "percentage_change": 3.979460847240058
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 810,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 445.0908716814018
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.5,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
