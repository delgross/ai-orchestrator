---
timestamp: 1767436887.390217
datetime: '2026-01-03T05:41:27.390217'
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
  anomaly_id: avg_response_time_1min_1767436887.390217
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 540.8337421994388
    baseline_value: 525.1700416687996
    deviation: 2.414030553881965
    severity: warning
    percentage_change: 2.9825959761272034
  system_state:
    active_requests: 7
    completed_requests_1min: 694
    error_rate_1min: 0.0
    avg_response_time_1min: 540.8337421994388
  metadata: {}
  efficiency:
    requests_per_second: 11.566666666666666
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 540.83
- **Baseline Value**: 525.17
- **Deviation**: 2.41 standard deviations
- **Change**: +3.0%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 694
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 540.83ms

### Efficiency Metrics

- **Requests/sec**: 11.57
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 540.8337421994388,
    "baseline_value": 525.1700416687996,
    "deviation": 2.414030553881965,
    "severity": "warning",
    "percentage_change": 2.9825959761272034
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 694,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 540.8337421994388
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 11.566666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
