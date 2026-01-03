---
timestamp: 1767373665.1961532
datetime: '2026-01-02T12:07:45.196153'
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
  anomaly_id: requests_per_second_1767373665.1961532
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.683333333333334
    baseline_value: 13.35
    deviation: 2.8571428571428505
    severity: warning
    percentage_change: 2.4968789013732877
  system_state:
    active_requests: 8
    completed_requests_1min: 821
    error_rate_1min: 0.0
    avg_response_time_1min: 753.1172906873287
  metadata: {}
  efficiency:
    requests_per_second: 13.683333333333334
    cache_hit_rate: 0.0
    queue_depth: 8
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.68
- **Baseline Value**: 13.35
- **Deviation**: 2.86 standard deviations
- **Change**: +2.5%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 8
- **Completed Requests (1min)**: 821
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 753.12ms

### Efficiency Metrics

- **Requests/sec**: 13.68
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 8

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.683333333333334,
    "baseline_value": 13.35,
    "deviation": 2.8571428571428505,
    "severity": "warning",
    "percentage_change": 2.4968789013732877
  },
  "system_state": {
    "active_requests": 8,
    "completed_requests_1min": 821,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 753.1172906873287
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.683333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 8
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
