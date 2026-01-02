---
timestamp: 1767354486.949503
datetime: '2026-01-02T06:48:06.949503'
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
  anomaly_id: avg_response_time_1min_1767354486.949503
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 439.1946429977874
    baseline_value: 447.61725347289314
    deviation: 2.0749752033454243
    severity: warning
    percentage_change: -1.881654563079925
  system_state:
    active_requests: 7
    completed_requests_1min: 835
    error_rate_1min: 0.0
    avg_response_time_1min: 439.1946429977874
  metadata: {}
  efficiency:
    requests_per_second: 13.916666666666666
    cache_hit_rate: 0.0
    queue_depth: 7
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 439.19
- **Baseline Value**: 447.62
- **Deviation**: 2.07 standard deviations
- **Change**: -1.9%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 7
- **Completed Requests (1min)**: 835
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 439.19ms

### Efficiency Metrics

- **Requests/sec**: 13.92
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 7

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 439.1946429977874,
    "baseline_value": 447.61725347289314,
    "deviation": 2.0749752033454243,
    "severity": "warning",
    "percentage_change": -1.881654563079925
  },
  "system_state": {
    "active_requests": 7,
    "completed_requests_1min": 835,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 439.1946429977874
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 13.916666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 7
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
