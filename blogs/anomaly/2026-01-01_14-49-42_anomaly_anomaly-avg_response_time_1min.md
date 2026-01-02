---
timestamp: 1767296982.369282
datetime: '2026-01-01T14:49:42.369282'
category: anomaly
severity: warning
title: 'Anomaly: avg_response_time_1min'
source: anomaly_detector
tags:
- anomaly
- avg_response_time_1min
- warning
resolution_status: open
suggested_actions: []
metadata:
  anomaly_id: avg_response_time_1min_1767296982.369282
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 412.98604831843744
    baseline_value: 474.4758164255243
    deviation: 2.442825055479429
    severity: warning
    percentage_change: -12.959515738930927
  system_state:
    active_requests: 7
    completed_requests_1min: 901
    error_rate_1min: 0.0
    avg_response_time_1min: 412.98604831843744
  metadata: {}
  efficiency:
    requests_per_second: 15.016666666666667
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 412.99
- **Baseline Value**: 474.48
- **Deviation**: 2.44 standard deviations
- **Change**: -13.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 901
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 412.99ms

### Efficiency Metrics

- **Requests/sec**: 15.02
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 412.98604831843744,
    "baseline_value": 474.4758164255243,
    "deviation": 2.442825055479429,
    "severity": "warning",
    "percentage_change": -12.959515738930927
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 901,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 412.98604831843744
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 15.016666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
