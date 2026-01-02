---
timestamp: 1767350886.25527
datetime: '2026-01-02T05:48:06.255270'
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
  anomaly_id: requests_per_second_1767350886.25527
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.666666666666666
    baseline_value: 13.966666666666667
    deviation: 1.5000000000000089
    severity: warning
    percentage_change: -2.1479713603818666
  system_state:
    active_requests: 6
    completed_requests_1min: 820
    error_rate_1min: 0.0
    avg_response_time_1min: 450.4752615603005
  metadata: {}
  efficiency:
    requests_per_second: 13.666666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.67
- **Baseline Value**: 13.97
- **Deviation**: 1.50 standard deviations
- **Change**: -2.1%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 820
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 450.48ms

### Efficiency Metrics

- **Requests/sec**: 13.67
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.666666666666666,
    "baseline_value": 13.966666666666667,
    "deviation": 1.5000000000000089,
    "severity": "warning",
    "percentage_change": -2.1479713603818666
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 820,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 450.4752615603005
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.666666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
