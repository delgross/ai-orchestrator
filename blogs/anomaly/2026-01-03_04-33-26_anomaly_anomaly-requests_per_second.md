---
timestamp: 1767432806.5291378
datetime: '2026-01-03T04:33:26.529138'
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
  anomaly_id: requests_per_second_1767432806.5291378
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.583333333333334
    baseline_value: 11.383333333333333
    deviation: 1.5000000000000133
    severity: warning
    percentage_change: 1.756954612005866
  system_state:
    active_requests: 6
    completed_requests_1min: 695
    error_rate_1min: 0.0
    avg_response_time_1min: 529.4053667740856
  metadata: {}
  efficiency:
    requests_per_second: 11.583333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.58
- **Baseline Value**: 11.38
- **Deviation**: 1.50 standard deviations
- **Change**: +1.8%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 695
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 529.41ms

### Efficiency Metrics

- **Requests/sec**: 11.58
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.583333333333334,
    "baseline_value": 11.383333333333333,
    "deviation": 1.5000000000000133,
    "severity": "warning",
    "percentage_change": 1.756954612005866
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 695,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 529.4053667740856
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.583333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
