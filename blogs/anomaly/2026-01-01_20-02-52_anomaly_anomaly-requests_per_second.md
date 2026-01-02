---
timestamp: 1767315772.362672
datetime: '2026-01-01T20:02:52.362672'
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
  anomaly_id: requests_per_second_1767315772.362672
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.366666666666666
    baseline_value: 2.9
    deviation: 2.0
    severity: warning
    percentage_change: 85.0574712643678
  system_state:
    active_requests: 1
    completed_requests_1min: 322
    error_rate_1min: 0.0
    avg_response_time_1min: 248.39839802025267
  metadata: {}
  efficiency:
    requests_per_second: 5.366666666666666
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.37
- **Baseline Value**: 2.90
- **Deviation**: 2.00 standard deviations
- **Change**: +85.1%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 322
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 248.40ms

### Efficiency Metrics

- **Requests/sec**: 5.37
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 5.366666666666666,
    "baseline_value": 2.9,
    "deviation": 2.0,
    "severity": "warning",
    "percentage_change": 85.0574712643678
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 322,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 248.39839802025267
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.366666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
