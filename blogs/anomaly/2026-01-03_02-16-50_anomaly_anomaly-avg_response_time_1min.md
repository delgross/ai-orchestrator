---
timestamp: 1767424610.427126
datetime: '2026-01-03T02:16:50.427126'
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
  anomaly_id: avg_response_time_1min_1767424610.427126
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 543.0011483425266
    baseline_value: 483.7927369061362
    deviation: 1.5570880792224193
    severity: warning
    percentage_change: 12.238383696090452
  system_state:
    active_requests: 7
    completed_requests_1min: 852
    error_rate_1min: 0.0
    avg_response_time_1min: 543.0011483425266
  metadata: {}
  efficiency:
    requests_per_second: 14.2
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 543.00
- **Baseline Value**: 483.79
- **Deviation**: 1.56 standard deviations
- **Change**: +12.2%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 852
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 543.00ms

### Efficiency Metrics

- **Requests/sec**: 14.20
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 543.0011483425266,
    "baseline_value": 483.7927369061362,
    "deviation": 1.5570880792224193,
    "severity": "warning",
    "percentage_change": 12.238383696090452
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 852,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 543.0011483425266
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.2,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
