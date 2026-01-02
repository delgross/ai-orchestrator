---
timestamp: 1767368790.950924
datetime: '2026-01-02T10:46:30.950924'
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
  anomaly_id: requests_per_second_1767368790.950924
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 9.75
    baseline_value: 11.5
    deviation: 2.0588235294117654
    severity: warning
    percentage_change: -15.217391304347828
  system_state:
    active_requests: 12
    completed_requests_1min: 585
    error_rate_1min: 0.0
    avg_response_time_1min: 1834.8405418232974
  metadata: {}
  efficiency:
    requests_per_second: 9.75
    cache_hit_rate: 0.0
    queue_depth: 12
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 9.75
- **Baseline Value**: 11.50
- **Deviation**: 2.06 standard deviations
- **Change**: -15.2%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 12
- **Completed Requests (1min)**: 585
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1834.84ms

### Efficiency Metrics

- **Requests/sec**: 9.75
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 12

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 9.75,
    "baseline_value": 11.5,
    "deviation": 2.0588235294117654,
    "severity": "warning",
    "percentage_change": -15.217391304347828
  },
  "system_state": {
    "active_requests": 12,
    "completed_requests_1min": 585,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1834.8405418232974
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 9.75,
    "cache_hit_rate": 0.0,
    "queue_depth": 12
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
