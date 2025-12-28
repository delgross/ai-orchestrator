---
timestamp: 1766882045.250726
datetime: '2025-12-27T19:34:05.250726'
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
  anomaly_id: requests_per_second_1766882045.250726
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 2.9
    baseline_value: 2.4307499999999997
    deviation: 5.657111857700361
    severity: warning
    percentage_change: 19.304741334978925
  system_state:
    active_requests: 0
    completed_requests_1min: 174
    error_rate_1min: 0.0
    avg_response_time_1min: 190.02786998091074
  metadata: {}
  efficiency:
    requests_per_second: 2.9
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 2.90
- **Baseline Value**: 2.43
- **Deviation**: 5.66 standard deviations
- **Change**: +19.3%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 174
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 190.03ms

### Efficiency Metrics

- **Requests/sec**: 2.90
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 2.9,
    "baseline_value": 2.4307499999999997,
    "deviation": 5.657111857700361,
    "severity": "warning",
    "percentage_change": 19.304741334978925
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 174,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 190.02786998091074
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.9,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
