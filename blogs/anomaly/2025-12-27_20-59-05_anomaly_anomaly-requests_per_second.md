---
timestamp: 1766887145.520193
datetime: '2025-12-27T20:59:05.520193'
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
  anomaly_id: requests_per_second_1766887145.520193
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 0.9666666666666667
    baseline_value: 2.3552166666666667
    deviation: 4.195995728851903
    severity: warning
    percentage_change: -58.95635928753901
  system_state:
    active_requests: 1
    completed_requests_1min: 58
    error_rate_1min: 0.0
    avg_response_time_1min: 30.286850600407043
  metadata: {}
  efficiency:
    requests_per_second: 0.9666666666666667
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 0.97
- **Baseline Value**: 2.36
- **Deviation**: 4.20 standard deviations
- **Change**: -59.0%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 58
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 30.29ms

### Efficiency Metrics

- **Requests/sec**: 0.97
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 0.9666666666666667,
    "baseline_value": 2.3552166666666667,
    "deviation": 4.195995728851903,
    "severity": "warning",
    "percentage_change": -58.95635928753901
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 58,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 30.286850600407043
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
