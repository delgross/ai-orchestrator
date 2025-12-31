---
timestamp: 1767167826.84262
datetime: '2025-12-31T02:57:06.842620'
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
  anomaly_id: avg_response_time_1min_1767167826.84262
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 112.83652535800276
    baseline_value: 99.9793224647397
    deviation: 1.5910671645757137
    severity: warning
    percentage_change: 12.859861995761666
  system_state:
    active_requests: 0
    completed_requests_1min: 29
    error_rate_1min: 0.0
    avg_response_time_1min: 112.83652535800276
  metadata: {}
  efficiency:
    requests_per_second: 0.48333333333333334
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 112.84
- **Baseline Value**: 99.98
- **Deviation**: 1.59 standard deviations
- **Change**: +12.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 29
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 112.84ms

### Efficiency Metrics

- **Requests/sec**: 0.48
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 112.83652535800276,
    "baseline_value": 99.9793224647397,
    "deviation": 1.5910671645757137,
    "severity": "warning",
    "percentage_change": 12.859861995761666
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 29,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 112.83652535800276
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.48333333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
