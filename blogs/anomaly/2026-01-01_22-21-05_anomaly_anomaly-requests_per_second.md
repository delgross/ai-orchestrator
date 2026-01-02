---
timestamp: 1767324065.728846
datetime: '2026-01-01T22:21:05.728846'
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
  anomaly_id: requests_per_second_1767324065.728846
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 13.383333333333333
    baseline_value: 13.55
    deviation: 1.6666666666666845
    severity: warning
    percentage_change: -1.2300123001230099
  system_state:
    active_requests: 6
    completed_requests_1min: 803
    error_rate_1min: 0.0
    avg_response_time_1min: 451.8647282981635
  metadata: {}
  efficiency:
    requests_per_second: 13.383333333333333
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 13.38
- **Baseline Value**: 13.55
- **Deviation**: 1.67 standard deviations
- **Change**: -1.2%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 803
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 451.86ms

### Efficiency Metrics

- **Requests/sec**: 13.38
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 13.383333333333333,
    "baseline_value": 13.55,
    "deviation": 1.6666666666666845,
    "severity": "warning",
    "percentage_change": -1.2300123001230099
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 803,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 451.8647282981635
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.383333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
