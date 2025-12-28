---
timestamp: 1766866924.2650619
datetime: '2025-12-27T15:22:04.265062'
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
  anomaly_id: avg_response_time_1min_1766866924.2650619
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 8.341477134011008
    baseline_value: 121.31381636996174
    deviation: 4.075983887963246
    severity: warning
    percentage_change: -93.12405018355648
  system_state:
    active_requests: 0
    completed_requests_1min: 55
    error_rate_1min: 0.0
    avg_response_time_1min: 8.341477134011008
  metadata: {}
  efficiency:
    requests_per_second: 0.9166666666666666
    cache_hit_rate: 0.0
    queue_depth: 0
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 8.34
- **Baseline Value**: 121.31
- **Deviation**: 4.08 standard deviations
- **Change**: -93.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 0
- **Completed Requests (1min)**: 55
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 8.34ms

### Efficiency Metrics

- **Requests/sec**: 0.92
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 0

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 8.341477134011008,
    "baseline_value": 121.31381636996174,
    "deviation": 4.075983887963246,
    "severity": "warning",
    "percentage_change": -93.12405018355648
  },
  "system_state": {
    "active_requests": 0,
    "completed_requests_1min": 55,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 8.341477134011008
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 0.9166666666666666,
    "cache_hit_rate": 0.0,
    "queue_depth": 0
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
