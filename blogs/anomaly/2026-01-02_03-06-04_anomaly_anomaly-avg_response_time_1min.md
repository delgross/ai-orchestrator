---
timestamp: 1767341164.8683589
datetime: '2026-01-02T03:06:04.868359'
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
  anomaly_id: avg_response_time_1min_1767341164.8683589
structured_data:
  anomaly:
    metric_name: avg_response_time_1min
    current_value: 423.76818673770754
    baseline_value: 437.3776737465916
    deviation: 1.7144292573856816
    severity: warning
    percentage_change: -3.111609902788303
  system_state:
    active_requests: 6
    completed_requests_1min: 849
    error_rate_1min: 0.0
    avg_response_time_1min: 423.76818673770754
  metadata: {}
  efficiency:
    requests_per_second: 14.15
    cache_hit_rate: 0.0
    queue_depth: 6
  resource_usage:
    error: psutil not available
---

# Anomaly: avg_response_time_1min

An anomaly was detected in the **avg_response_time_1min** metric.

## Details

- **Current Value**: 423.77
- **Baseline Value**: 437.38
- **Deviation**: 1.71 standard deviations
- **Change**: -3.1%
- **Severity**: WARNING

**What this means**: Average response time over the last minute. High values indicate slow system performance.

## System Context

- **Active Requests**: 6
- **Completed Requests (1min)**: 849
- **Error Rate (1min)**: 0.00%
- **Avg Response Time (1min)**: 423.77ms

### Efficiency Metrics

- **Requests/sec**: 14.15
- **Cache Hit Rate**: 0.0%
- **Queue Depth**: 6

### Resource Usage



## Structured Data

```json
{
  "anomaly": {
    "metric_name": "avg_response_time_1min",
    "current_value": 423.76818673770754,
    "baseline_value": 437.3776737465916,
    "deviation": 1.7144292573856816,
    "severity": "warning",
    "percentage_change": -3.111609902788303
  },
  "system_state": {
    "active_requests": 6,
    "completed_requests_1min": 849,
    "error_rate_1min": 0.0,
    "avg_response_time_1min": 423.76818673770754
  },
  "metadata": {},
  "efficiency": {
    "requests_per_second": 14.15,
    "cache_hit_rate": 0.0,
    "queue_depth": 6
  },
  "resource_usage": {
    "error": "psutil not available"
  }
}
```
