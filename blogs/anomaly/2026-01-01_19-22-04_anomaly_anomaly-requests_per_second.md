---
timestamp: 1767313324.6042051
datetime: '2026-01-01T19:22:04.604205'
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
  anomaly_id: requests_per_second_1767313324.6042051
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.116666666666666
    baseline_value: 2.9
    deviation: 1.873239436619718
    severity: warning
    percentage_change: 76.43678160919539
  system_state:
    active_requests: 1
    completed_requests_1min: 307
    error_rate_1min: 0.0
    avg_response_time_1min: 219.25780050917635
  metadata: {}
  efficiency:
    requests_per_second: 5.116666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.12
- **Baseline Value**: 2.90
- **Deviation**: 1.87 standard deviations
- **Change**: +76.4%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 307
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 219.26ms

### Efficiency Metrics

- **Requests/sec**: 5.12
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 5.116666666666666,
    "baseline_value": 2.9,
    "deviation": 1.873239436619718,
    "severity": "warning",
    "percentage_change": 76.43678160919539
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 307,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 219.25780050917635
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.116666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
