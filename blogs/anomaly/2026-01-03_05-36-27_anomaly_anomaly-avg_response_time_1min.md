---
timestamp: 1767436587.2938292
datetime: '2026-01-03T05:36:27.293829'
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
  anomaly_id: avg_response_time_1min_1767436587.2938292
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 559.9310519145085
    baseline_value: 531.5972718261403
    deviation: 2.0311096042728836
    severity: warning
    percentage_change: 5.329933314186546
  system_state:
    active_requests: 6
    completed_requests_1min: 650
    error_rate_1min: 0.0
    avg_response_time_1min: 559.9310519145085
  metadata: {}
  efficiency:
    requests_per_second: 10.833333333333334
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 559.93
- **Baseline Value**: 531.60
- **Deviation**: 2.03 standard deviations
- **Change**: +5.3%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 650
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 559.93ms

### Efficiency Metrics

- **Requests/sec**: 10.83
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 559.9310519145085,
    "baseline_value": 531.5972718261403,
    "deviation": 2.0311096042728836,
    "severity": "warning",
    "percentage_change": 5.329933314186546
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 650,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 559.9310519145085
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 10.833333333333334,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
