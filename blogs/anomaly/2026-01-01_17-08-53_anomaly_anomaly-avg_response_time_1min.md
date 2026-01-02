---
timestamp: 1767305333.7596061
datetime: '2026-01-01T17:08:53.759606'
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
  anomaly_id: avg_response_time_1min_1767305333.7596061
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 374.17638436803276
    baseline_value: 315.94229926747727
    deviation: 1.5952479911523547
    severity: warning
    percentage_change: 18.43187355272566
  system_state:
    active_requests: 2
    completed_requests_1min: 265
    error_rate_1min: 0.0
    avg_response_time_1min: 374.17638436803276
  metadata: {}
  efficiency:
    requests_per_second: 4.416666666666667
    cache_hit_rate: 0.0
    queue_depth: 2
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 374.18
- **Baseline Value**: 315.94
- **Deviation**: 1.60 standard deviations
- **Change**: +18.4%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 2
- **Completed Requests (1min)**: 265
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 374.18ms

### Efficiency Metrics

- **Requests/sec**: 4.42
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 2

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 374.17638436803276,
    "baseline_value": 315.94229926747727,
    "deviation": 1.5952479911523547,
    "severity": "warning",
    "percentage_change": 18.43187355272566
  },
  "system_state": {
    "active_requests": 2,
    "completed_requests_1min": 265,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 374.17638436803276
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 4.416666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 2
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
