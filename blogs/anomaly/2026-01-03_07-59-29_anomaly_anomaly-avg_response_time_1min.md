---
timestamp: 1767445169.126614
datetime: '2026-01-03T07:59:29.126614'
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
  anomaly_id: avg_response_time_1min_1767445169.126614
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 557.1592152118683
    baseline_value: 458.117733567448
    deviation: 2.328198336148629
    severity: warning
    percentage_change: 21.61922021074492
  system_state:
    active_requests: 7
    completed_requests_1min: 400
    error_rate_1min: 0.0
    avg_response_time_1min: 557.1592152118683
  metadata: {}
  efficiency:
    requests_per_second: 6.666666666666667
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 557.16
- **Baseline Value**: 458.12
- **Deviation**: 2.33 standard deviations
- **Change**: +21.6%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 400
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 557.16ms

### Efficiency Metrics

- **Requests/sec**: 6.67
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 557.1592152118683,
    "baseline_value": 458.117733567448,
    "deviation": 2.328198336148629,
    "severity": "warning",
    "percentage_change": 21.61922021074492
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 400,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 557.1592152118683
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 6.666666666666667,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
