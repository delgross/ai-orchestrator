---
timestamp: 1767368250.842134
datetime: '2026-01-02T10:37:30.842134'
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
  anomaly_id: requests_per_second_1767368250.842134
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 10.816666666666666
    baseline_value: 6.983333333333333
    deviation: 1.7829457364341081
    severity: warning
    percentage_change: 54.8926014319809
  system_state:
    active_requests: 16
    completed_requests_1min: 649
    error_rate_1min: 0.0
    avg_response_time_1min: 1552.0410317301935
  metadata: {}
  efficiency:
    requests_per_second: 10.816666666666666
    cache_hit_rate: 0.0
    queue_depth: 16
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 10.82
- **Baseline Value**: 6.98
- **Deviation**: 1.78 standard deviations
- **Change**: +54.9%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 16
- **Completed Requests (1min)**: 649
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1552.04ms

### Efficiency Metrics

- **Requests/sec**: 10.82
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 16

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 10.816666666666666,
    "baseline_value": 6.983333333333333,
    "deviation": 1.7829457364341081,
    "severity": "warning",
    "percentage_change": 54.8926014319809
  },
  "system_state": {
    "active_requests": 16,
    "completed_requests_1min": 649,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1552.0410317301935
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.816666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 16
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
