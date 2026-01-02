---
timestamp: 1767308919.4261801
datetime: '2026-01-01T18:08:39.426180'
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
  anomaly_id: requests_per_second_1767308919.4261801
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 7.083333333333333
    baseline_value: 3.2333333333333334
    deviation: 1.711111111111111
    severity: warning
    percentage_change: 119.07216494845359
  system_state:
    active_requests: 1
    completed_requests_1min: 425
    error_rate_1min: 0.0
    avg_response_time_1min: 233.7769272748162
  metadata: {}
  efficiency:
    requests_per_second: 7.083333333333333
    cache_hit_rate: 0.0
    queue_depth: 1
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 7.08
- **Baseline Value**: 3.23
- **Deviation**: 1.71 standard deviations
- **Change**: +119.1%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 1
- **Completed Requests (1min)**: 425
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 233.78ms

### Efficiency Metrics

- **Requests/sec**: 7.08
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 1

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 7.083333333333333,
    "baseline_value": 3.2333333333333334,
    "deviation": 1.711111111111111,
    "severity": "warning",
    "percentage_change": 119.07216494845359
  },
  "system_state": {
    "active_requests": 1,
    "completed_requests_1min": 425,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 233.7769272748162
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 7.083333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 1
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
