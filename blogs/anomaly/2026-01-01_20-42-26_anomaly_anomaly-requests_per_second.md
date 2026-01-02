---
timestamp: 1767318146.135339
datetime: '2026-01-01T20:42:26.135339'
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
  anomaly_id: requests_per_second_1767318146.135339
structured_data:
  anomaly:
    metric_name: requests_per_second
    current_value: 5.883333333333334
    baseline_value: 2.0833333333333335
    deviation: 2.350515463917526
    severity: warning
    percentage_change: 182.4
  system_state:
    active_requests: 2
    completed_requests_1min: 353
    error_rate_1min: 0.0
    avg_response_time_1min: 116.38610423793199
  metadata: {}
  efficiency:
    requests_per_second: 5.883333333333334
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: requests_per_second

An anomaly was detected in the **requests_per_second** metric.

## Details

- **Current Value**: 5.88
- **Baseline Value**: 2.08
- **Deviation**: 2.35 standard deviations
- **Change**: +182.4%
- **Severity**: WARNING

**What this means**: Request throughput. Low values may indicate system degradation.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 353
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 116.39ms

### Efficiency Metrics

- **Requests/sec**: 5.88
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "requests_per_second",
    "current_value": 5.883333333333334,
    "baseline_value": 2.0833333333333335,
    "deviation": 2.350515463917526,
    "severity": "warning",
    "percentage_change": 182.4
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 353,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 116.38610423793199
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 5.883333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
