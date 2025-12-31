---
timestamp: 1767152944.53133
datetime: '2025-12-30T22:49:04.531330'
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
  anomaly_id: avg_response_time_1min_1767152944.53133
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 92.45027229189873
    baseline_value: 85.23501210267159
    deviation: 2.5338698902360157
    severity: warning
    percentage_change: 8.465136580887496
  system_state:
    active_requests: 0
    completed_requests_1min: 128
    error_rate_1min: 0.0
    avg_response_time_1min: 92.45027229189873
  metadata: {}
  efficiency:
    requests_per_second: 2.1333333333333333
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 92.45
- **Baseline Value**: 85.24
- **Deviation**: 2.53 standard deviations
- **Change**: +8.5%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 128
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 92.45ms

### Efficiency Metrics

- **Requests/sec**: 2.13
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 92.45027229189873,
    "baseline_value": 85.23501210267159,
    "deviation": 2.5338698902360157,
    "severity": "warning",
    "percentage_change": 8.465136580887496
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 128,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 92.45027229189873
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 2.1333333333333333,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
