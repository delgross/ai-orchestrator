---
timestamp: 1767263087.7484539
datetime: '2026-01-01T05:24:47.748454'
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
  anomaly_id: avg_response_time_1min_1767263087.7484539
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 938.188910484314
    baseline_value: 552.9772154986858
    deviation: 1.6074203695374418
    severity: warning
    percentage_change: 69.66140451885283
  system_state:
    active_requests: 0
    completed_requests_1min: 82
    error_rate_1min: 0.0
    avg_response_time_1min: 938.188910484314
  metadata: {}
  efficiency:
    requests_per_second: 1.3666666666666667
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 938.19
- **Baseline Value**: 552.98
- **Deviation**: 1.61 standard deviations
- **Change**: +69.7%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 82
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 938.19ms

### Efficiency Metrics

- **Requests/sec**: 1.37
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 938.188910484314,
    "baseline_value": 552.9772154986858,
    "deviation": 1.6074203695374418,
    "severity": "warning",
    "percentage_change": 69.66140451885283
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 82,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 938.188910484314
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 1.3666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
