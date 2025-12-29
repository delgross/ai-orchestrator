---
timestamp: 1767041061.664415
datetime: '2025-12-29T15:44:21.664415'
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
  anomaly_id: requests_per_second_1767041061.664415
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.21666666666666667
    baseline_value: 0.020490867579908676
    deviation: 5.4865597344452945
    severity: warning
    percentage_change: 957.3816155988858
  system_state:
    active_requests: 4
    completed_requests_1min: 13
    error_rate_1min: 0.0
    avg_response_time_1min: 19142.35580884493
  metadata: {}
  efficiency:
    requests_per_second: 0.21666666666666667
    cache_hit_rate: 0.0
    queue_depth: 4
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.22
- **Baseline Value**: 0.02
- **Deviation**: 5.49 standard deviations
- **Change**: +957.4%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 4
- **Completed Requests (1min)**: 13
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 19142.36ms

### Efficiency Metrics

- **Requests/sec**: 0.22
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 4

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 0.21666666666666667,
    "baseline_value": 0.020490867579908676,
    "deviation": 5.4865597344452945,
    "severity": "warning",
    "percentage_change": 957.3816155988858
  },
  "system_state": {
    "active_requests": 4,
    "completed_requests_1min": 13,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 19142.35580884493
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.21666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 4
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
