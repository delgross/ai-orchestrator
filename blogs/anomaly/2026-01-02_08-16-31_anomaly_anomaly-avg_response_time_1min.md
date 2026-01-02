---
timestamp: 1767359791.7511628
datetime: '2026-01-02T08:16:31.751163'
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
  anomaly_id: avg_response_time_1min_1767359791.7511628
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 1139.7581082401853
    baseline_value: 814.6583303789324
    deviation: 2.256267002275635
    severity: warning
    percentage_change: 39.906273064197975
  system_state:
    active_requests: 2
    completed_requests_1min: 132
    error_rate_1min: 0.0
    avg_response_time_1min: 1139.7581082401853
  metadata: {}
  efficiency:
    requests_per_second: 2.2
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 1139.76
- **Baseline Value**: 814.66
- **Deviation**: 2.26 standard deviations
- **Change**: +39.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 132
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 1139.76ms

### Efficiency Metrics

- **Requests/sec**: 2.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 1139.7581082401853,
    "baseline_value": 814.6583303789324,
    "deviation": 2.256267002275635,
    "severity": "warning",
    "percentage_change": 39.906273064197975
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 132,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 1139.7581082401853
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
