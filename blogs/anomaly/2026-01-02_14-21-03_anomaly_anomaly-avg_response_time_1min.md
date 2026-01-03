---
timestamp: 1767381663.883727
datetime: '2026-01-02T14:21:03.883727'
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
  anomaly_id: avg_response_time_1min_1767381663.883727
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1108.6310004556417
    baseline_value: 979.8331109304277
    deviation: 1.630775469061542
    severity: warning
    percentage_change: 13.144880295268898
  system_state:
    active_requests: 10
    completed_requests_1min: 755
    error_rate_1min: 0.0
    avg_response_time_1min: 1108.6310004556417
  metadata: {}
  efficiency:
    requests_per_second: 12.583333333333334
    cache_hit_rate: 0.0
    queue_depth: 10
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1108.63
- **Baseline Value**: 979.83
- **Deviation**: 1.63 standard deviations
- **Change**: +13.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 10
- **Completed Requests (1min)**: 755
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1108.63ms

### Efficiency Metrics

- **Requests/sec**: 12.58
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 10

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1108.6310004556417,
    "baseline_value": 979.8331109304277,
    "deviation": 1.630775469061542,
    "severity": "warning",
    "percentage_change": 13.144880295268898
  },
  "system_state": {
    "active_requests": 10,
    "completed_requests_1min": 755,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1108.6310004556417
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 12.583333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 10
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
