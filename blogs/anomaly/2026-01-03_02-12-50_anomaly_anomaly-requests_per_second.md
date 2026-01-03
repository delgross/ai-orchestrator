---
timestamp: 1767424370.362744
datetime: '2026-01-03T02:12:50.362744'
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
  anomaly_id: requests_per_second_1767424370.362744
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 14.3
    baseline_value: 14.066666666666666
    deviation: 1.7500000000000133
    severity: warning
    percentage_change: 1.658767772511855
  system_state:
    active_requests: 7
    completed_requests_1min: 858
    error_rate_1min: 0.0
    avg_response_time_1min: 504.6991095954166
  metadata: {}
  efficiency:
    requests_per_second: 14.3
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 14.30
- **Baseline Value**: 14.07
- **Deviation**: 1.75 standard deviations
- **Change**: +1.7%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 858
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 504.70ms

### Efficiency Metrics

- **Requests/sec**: 14.30
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 14.3,
    "baseline_value": 14.066666666666666,
    "deviation": 1.7500000000000133,
    "severity": "warning",
    "percentage_change": 1.658767772511855
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 858,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 504.6991095954166
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.3,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
