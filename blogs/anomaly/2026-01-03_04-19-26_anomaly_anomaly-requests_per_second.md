---
timestamp: 1767431966.375236
datetime: '2026-01-03T04:19:26.375236'
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
  anomaly_id: requests_per_second_1767431966.375236
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 11.416666666666666
    baseline_value: 11.116666666666667
    deviation: 1.9999999999999882
    severity: warning
    percentage_change: 2.6986506746626593
  system_state:
    active_requests: 6
    completed_requests_1min: 685
    error_rate_1min: 0.0
    avg_response_time_1min: 523.5416990127006
  metadata: {}
  efficiency:
    requests_per_second: 11.416666666666666
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 11.42
- **Baseline Value**: 11.12
- **Deviation**: 2.00 standard deviations
- **Change**: +2.7%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 685
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 523.54ms

### Efficiency Metrics

- **Requests/sec**: 11.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 11.416666666666666,
    "baseline_value": 11.116666666666667,
    "deviation": 1.9999999999999882,
    "severity": "warning",
    "percentage_change": 2.6986506746626593
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 685,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 523.5416990127006
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.416666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
